from concurrent import futures
import json
import secrets
import threading
import time
import traceback
import grpc
from protos import bank_pb2
from protos import bank_pb2_grpc
import time
from backend import notifyClient
from backend import connectSql
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
import base64, os
from Crypto.Signature import pkcs1_15

with open("certs/bank-key.pem", "r") as src:
    bank_key = RSA.importKey(src.read(), passphrase='testbank')
    
with open("certs/pis-cert.pem", "r") as src:
    pis_cert = RSA.importKey(src.read())

with open("certs/webserver-cert.pem", "r") as src: 
    webserver_cert = RSA.importKey(src.read())

def VerifyNonce(hashedNonceEncrypted,encryptedNonce,encryptedKey, token, hashedData):
    try:       
        #Get Key simetric
        cipher = PKCS1_OAEP.new(bank_key)
        simetric_key = cipher.decrypt(base64.b64decode(encryptedKey.encode('utf-8')))
    
        sig = json.loads(simetric_key.decode("utf-8"))
        sig_key = base64.b64decode(sig["key"].encode('utf-8'))
        iv = base64.b64decode(sig["iv"].encode('utf-8'))
        
        #Decrypt nonce with Key simetric
        cipher = AES.new(sig_key, AES.MODE_CFB, iv)
        nonce_bytes = cipher.decrypt(base64.b64decode(encryptedNonce.encode('utf-8')))
        nonce = nonce_bytes.decode('utf-8')
        
        #Hash nonce + hashedData
        digest = SHA256.new()
        digest.update(nonce_bytes + hashedData.encode('utf-8'))
    
        #Check if Hash(nonce + hashedData) = {Hash(nonce + hashedData)}kprivatePIS
        try:
            hashedNonce = base64.b64decode(hashedNonceEncrypted.encode('utf-8'))     
            pkcs1_15.new(pis_cert).verify(digest, hashedNonce)

        except (ValueError):
            return False


        if connectSql.verifyFreshness(nonce, token) == True:
            connectSql.deleteNonce(token)
            return True
        else:
            return False 

    except Exception as e:
        traceback.print_exc()


def DecryptData(hashedDataEncrypted, encryptedData, encryptedKey):
    #Get Key simetric
    cipher = PKCS1_OAEP.new(bank_key)
    simetric_key = cipher.decrypt(base64.b64decode(encryptedKey.encode('utf-8')))

    try:
        sig = json.loads(simetric_key.decode("utf-8"))
        sig_key = base64.b64decode(sig["key"].encode('utf-8'))
        iv = base64.b64decode(sig["iv"].encode('utf-8'))

        #Decrypt data with Key simetric
        cipher = AES.new(sig_key, AES.MODE_CFB, iv)
        data_bytes = cipher.decrypt(base64.b64decode(encryptedData.encode('utf-8')))
        data = data_bytes.decode('utf-8')
    except Exception as e:
        print(e)

    json_data = json.loads(data)

    #Hash data to verify 
    digest = SHA256.new()
    digest.update(data_bytes)

    #Check if Hash(data) = {Hash(data)}kprivateWebserver
    try:
        hashedData = base64.b64decode(hashedDataEncrypted.encode('utf-8'))     
        pkcs1_15.new(webserver_cert).verify(digest, hashedData)
    except (ValueError):
        return None

    return json_data


class Listener(bank_pb2_grpc.bankServicer):
    """The listener function implemests the rpc call as described in the .proto file"""

    def __init__(self):
        self.counter = 0
        self.last_print_time = time.time()

    def __str__(self):
        return self.__class__.__name__

    def getNonce(self, request, context):
                
        _nonce = secrets.token_urlsafe()

        connectSql.createFreshness(request.token, _nonce)
   
        print("-----------Responding to Nonce Request from PIS--------------")
        return bank_pb2.NonceReply(nonce = _nonce)


    def confirmTransaction(self, request, context):
        print("-----------Transaction Info received from PIS--------------")

        nonce= request.nonce
        if VerifyNonce(nonce.hashedNonce, nonce.encryptedNonce, nonce.encryptedKey, request.token, request.data.hashedData) == False:
            print("-----------Invalid Verification on Nonce--------------")
            return bank_pb2.PispReply(status= "invalid")

        #Decriptar info do webserver 
        data = request.data
        json_data = DecryptData(data.hashedData, data.encryptedData, data.encryptedKey)
        if json_data == None:
            return bank_pb2.PispReply(status= "invalid")

        name = json_data["name"]
        email = json_data["email"]
        value = json_data["value"]
        store_name = json_data["store_name"]
        store_iban = json_data["store_iban"]

        connectSql.createTransaction(request.iban, store_iban, int(float(value)), request.token)
        
        url = "https://sirsbank.com/home?token=" + request.token
        email = connectSql.getEmail(request.iban) 
        res = notifyClient.sendEmail(email, url, store_name, value )
        if res == None:
            return bank_pb2.PispReply(status= "cancelled")

        print("-----------Email sent for User confirmation--------------")

        while 1:
            if connectSql.checkStatus(request.token) == "success":
                print("-----------Transaction was done successfuly--------------")
                
                users = connectSql.getUsers()
                for user in users:
                    print("IBAN: " + user[0] + ", Name: " + user[1] + "e-mail: " + user[2] + "balance: €" + str(user[3]))
                    
                return bank_pb2.PispReply(status= "success")
            elif connectSql.checkStatus(request.token) == "cancelled":
                print("-----------Transaction was canceled--------------")
                return bank_pb2.PispReply(status= "cancelled")
            time.sleep(1)
        

    

def serve():
    """The main serve function of the server.
    This opens the socket, and listens for incoming grpc conformant packets"""

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    bank_pb2_grpc.add_bankServicer_to_server(Listener(), server)

    with open("certs/bank-key.pem", "r") as src:
        bank_key = RSA.importKey(src.read(), passphrase="testbank")
        decrypted_key = bank_key.export_key("PEM",None,pkcs=8)

    with open('certs/bank-cert.pem', 'rb') as f:
        certificate_chain = f.read()
    
    with open('certs/ca-cert.pem', 'rb') as f:
        ca_cert = f.read()

    server_credentials = grpc.ssl_server_credentials( ( (decrypted_key, certificate_chain), ), ca_cert, require_client_auth=True)
    server.add_secure_port("192.168.56.12:2001", server_credentials)
    server.start()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        server.stop(0)