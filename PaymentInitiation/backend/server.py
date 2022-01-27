from concurrent import futures
import json
from os import stat
import secrets
import sqlite3
import threading
import time
import grpc
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
import base64, os
from Crypto.Signature import pkcs1_15


from . import server_pb2
from . import server_pb2_grpc

with open("certs/pis-key.pem", "r") as src:
    pis_key = RSA.importKey(src.read(), passphrase="testpis")
    
with open("certs/webserver-cert.pem", "r") as src:
    webserver_cert = RSA.importKey(src.read())

database = sqlite3.connect("db/pisp.sqlite")    
    
def VerifyNonce(nonce, token, hashedData):
    
    database = sqlite3.connect("db/pisp.sqlite")    

    hashedNonceEncrypted = nonce.hashedNonce
    encryptedNonce = nonce.encryptedNonce
    encryptedKey = nonce.encryptedKey
    
    cipher = PKCS1_OAEP.new(pis_key)
    symmetric_key = cipher.decrypt(base64.b64decode(encryptedKey.encode('utf-8')))

    sig = json.loads(symmetric_key.decode("utf-8"))
    sig_key = base64.b64decode(sig["key"].encode('utf-8'))
    iv = base64.b64decode(sig["iv"].encode('utf-8'))
    
    cipher = AES.new(sig_key, AES.MODE_CFB, iv)
    nonce_bytes = cipher.decrypt(base64.b64decode(encryptedNonce.encode('utf-8')))
    nonce = nonce_bytes.decode('utf-8')
    
    digest = SHA256.new()
    digest.update(nonce_bytes + hashedData.encode('utf-8'))
    
    try:
        hashedNonce = base64.b64decode(hashedNonceEncrypted.encode('utf-8'))
        pkcs1_15.new(webserver_cert).verify(digest, hashedNonce)
        
    except (ValueError): 
        return False  
    
    cur = database.cursor()
    sql = 'SELECT nonce FROM Nonce_table WHERE token = ?;'
    cur.execute(sql, (token,))
    res = cur.fetchone()
    
    if res[0] == nonce:
        cur.execute('DELETE FROM Nonce_table WHERE token = ?;', (token,))
        database.commit()
        return True
    else:
        return False
          

class Listener(server_pb2_grpc.PIServiceServicer):
    """The listener function implemests the rpc call as described in the .proto file"""

    def __init__(self):
        self.counter = 0
        self.last_print_time = time.time()

    def __str__(self):
        return self.__class__.__name__


    def getNonce(self, request, context):
        
        
        database = sqlite3.connect("db/pisp.sqlite")            
        cur = database.cursor()

        _nonce = secrets.token_urlsafe()

        sql = "INSERT OR REPLACE INTO Nonce_table VALUES (?, ?)"
        cur.execute(sql, (request.token, _nonce))
        database.commit()


        print("-----------Responding to Nonce Request from PIS--------------")
        return server_pb2.Nonce(nonce = _nonce)


    def requestURL(self, request, context):  
        if not VerifyNonce(request.nonce, request.token.token, request.data.hashedData):
            print("-----------Invalid verification of Nonce--------------")
            return server_pb2.URL(url = "erro")
        
        merchant_data = {"hashedData":request.data.hashedData, "encryptedData":request.data.encryptedData, "encryptedKey":request.data.encryptedKey}

        database = sqlite3.connect("db/pisp.sqlite")    
        sql = ' INSERT INTO Transactions (id,token,merchant,status,merchantData,iban) VALUES (NULL, ?, ?, "pending", ?,"0");'
        cur = database.cursor()
        cur.execute(sql, (request.token.token, request.token.merchantName, json.dumps(merchant_data)))
        database.commit()
        
        print("-----------Responding with url for Webserver--------------")
        return server_pb2.URL(url = "https://xptopaymentprovider.com/login?token=" + request.token.token)


    def requestConfirmation(self, request, context):
        print("-----------Responding with Transaction Status--------------")

        database = sqlite3.connect("db/pisp.sqlite")
        sql = 'SELECT status FROM Transactions WHERE token = ?;'
        cur = database.cursor()
        cur.execute(sql, (request.token,))

        res = cur.fetchone()

        if(res != None):
            return server_pb2.Confirmation(status = res[0])
        else:
            return server_pb2.Confirmation(status = "pending")


def serve():
    """The main serve function of the server.
    This opens the socket, and listens for incoming grpc conformant packets"""

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    server_pb2_grpc.add_PIServiceServicer_to_server(Listener(), server)
    
    with open("certs/pis-key.pem", "r") as src:
        pis_key = RSA.importKey(src.read(), passphrase="testpis")
        decrypted_key = pis_key.export_key("PEM",None,pkcs=8)
    
    with open('certs/pis-cert.pem', 'rb') as f:
        certificate_chain = f.read()

    with open('certs/ca-cert.pem', 'rb') as f:
        ca_cert = f.read()
        
    server_credentials = grpc.ssl_server_credentials( ( (decrypted_key, certificate_chain),), ca_cert, require_client_auth=True)
    
    server.add_secure_port("192.168.56.11:4001", server_credentials)
    server.start()
    
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        server.stop(0)