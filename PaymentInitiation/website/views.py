import json
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
import grpc
from werkzeug.security import generate_password_hash, check_password_hash
from protos import bank_pb2
import protos.bank_pb2_grpc
from website import connect_db, init_stub
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
import base64, os
from Crypto.Signature import pkcs1_15

views = Blueprint('views', __name__)

with open("certs/pis-key.pem", "r") as src:
    pis_key = RSA.importKey(src.read(), passphrase='testpis')
    
with open("certs/bank-cert.pem", "r") as src:
    bank_cert = RSA.importKey(src.read())


@views.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")


@views.route('/login', methods=['GET'])
def login():
    
    session["token"] = request.args.get("token")
    
    return render_template("login.html")

@views.route('/login', methods=['POST'])
def fill_bank_info():
    
    email = request.form.get('email')
    password = request.form.get('password')


    user = getUserFromDB(email)

    if user:
        iban = user[2]
        salt_user = user[1][-64:]
        password += salt_user

        if check_password_hash(user[1][:-64], password):
            #flash('Logged in successfully!', category='success')
            database = connect_db("db/pisp.sqlite")
            
            sql = 'UPDATE Transactions SET iban=? WHERE token = ?;'
            cur = database.cursor()
            cur.execute(sql, (iban, session["token"]))
            
            database.commit()
            
            return redirect(url_for('views.confirmTransaction'))
        else:
            flash('Incorrect password, try again.', category='error')
    else:
        flash('E-mail does not exist.', category='error')
        
    return render_template("login.html")


@views.route('/confirmtransaction', methods=['GET'])
def confirmTransaction():
    
    if not session["token"]:
        return render_template('error.html')
        
    database = connect_db("db/pisp.sqlite")
    sql = 'SELECT iban FROM Transactions WHERE token = ?;'
    cur = database.cursor()
    cur.execute(sql, (session["token"],))
    
    res = cur.fetchone()
    if not res:
        return render_template('error.html')
    
    _iban = res[0]
    
    return render_template("confirmtransaction.html", iban = _iban)


@views.route('/confirmtransaction', methods=['POST'])
def form():
    # Get data from form
    _token = session["token"]

    if  _token == None:
        return render_template("error.html")
    
    database = connect_db("db/pisp.sqlite")
    sql = 'SELECT merchant, status, merchantData, iban FROM Transactions status WHERE token = ?;'
    cur = database.cursor()
    cur.execute(sql, (_token,))

    res = cur.fetchone()
    
    if (res == None):
        return render_template("error.html")
    
    _iban = res[3]
    if (_iban == '0'):
        return render_template("error.html")
        
    merchantName = res[0]
    if res[1] != "pending":
        return render_template("error.html")
    
    stub = init_stub()
 
    (msg_nonce, msg_data) = BuildBankMessage(_token, res[2])
 
    bankrequest = bank_pb2.PispRequest(token = _token, iban = _iban, name = "user", nonce = msg_nonce, data = msg_data)
    print("-----------Send transaction info for Bank--------------")
    response = stub.confirmTransaction(bankrequest)
    print("-----------Received confirmation from Bank--------------")

    cur = database.cursor()
    if response.status == "success":
        sql = 'UPDATE Transactions SET status = "confirmed" WHERE token = ?;'
        cur.execute(sql, (_token,))
    else:
        sql = 'UPDATE Transactions SET status = "cancelled" WHERE token = ?;'
        cur.execute(sql, (_token,))
    
    database.commit()
    
    if response.status == "success":
        return render_template("transaction_successful.html")
    else:
        return render_template("transaction_failed.html")
    

def EncryptNonce(nonce, hashedData):
    #Sign with private key (hash(nonce))
    nonce_bytes = nonce.encode('utf-8')
    digest = SHA256.new()
    digest.update(nonce_bytes + hashedData.encode('utf-8'))
                
    hashedNonce = pkcs1_15.new(pis_key).sign(digest)

    #Encrypt Nonce with Symetric key of pis
    key = get_random_bytes(32)
    cipher = AES.new(key, AES.MODE_CFB)
    encryptedNonce = cipher.encrypt(nonce_bytes)

    #Encrypt Symetric key of pis with publick key of pis
    sym_key = {
        "key": base64.b64encode(key).decode('utf-8') ,
        "iv": base64.b64encode(cipher.iv).decode('utf-8') 
    }
    
    ks = json.dumps(sym_key)
        
    signer = PKCS1_OAEP.new(bank_cert)
    encryptedkey = signer.encrypt(ks.encode("utf-8"))
    
    return (hashedNonce, encryptedNonce, encryptedkey)


def BuildBankMessage(_token, merchantData):
    stub = init_stub()

    response = stub.getNonce(bank_pb2.NonceRequest(token= _token))
    print("-----------Get Nonce from Bank--------------")
    
    data = json.loads(merchantData)
    (hashedNonce, encryptedNonce, encryptedkey) = EncryptNonce(response.nonce, data["hashedData"])
        
    msg_nonce = bank_pb2.EncryptedNonce(hashedNonce = base64.b64encode(hashedNonce).decode('utf-8'),
                                        encryptedNonce = base64.b64encode(encryptedNonce).decode('utf-8'),
                                        encryptedKey =  base64.b64encode(encryptedkey).decode('utf-8'))
    
    msg_data = bank_pb2.EncryptedData( hashedData = data["hashedData"],
                                        encryptedData = data["encryptedData"],
                                        encryptedKey = data["encryptedKey"])
    
    return (msg_nonce, msg_data)

def getUserFromDB(email):
    
    database = connect_db("db/pisp.sqlite")
    sql = 'SELECT email, password, iban FROM Accounts WHERE email = ?;'
    cur = database.cursor()
    cur.execute(sql, (email,))

    return cur.fetchone()