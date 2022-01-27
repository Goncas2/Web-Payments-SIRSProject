from asyncio.proactor_events import constants
from flask import Blueprint, redirect, render_template, request,  jsonify, session, url_for
from flask.helpers import flash
from flask_login import  current_user, login_required
from . import db
from .models import Transaction
from .models import User
from website import init_stub
from werkzeug.security import generate_password_hash
import client_pb2
import json
import secrets
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
import base64

views = Blueprint('views', __name__)
stub = init_stub()
error = "Error"
ok = "ok"


with open("certs/webserver-key.pem", "r") as src:
    webserver_key = RSA.importKey(src.read(), passphrase="testwebserver")

with open("certs/ca-cert.pem", "r") as src:
    webserver_cert = RSA.importKey(src.read())

with open("certs/pis-cert.pem", "r") as src:
    pis_cert = RSA.importKey(src.read())

with open("certs/bank-cert.pem", "r") as src:
    bank_cert = RSA.importKey(src.read())

@views.route('/', methods=['GET', 'POST'])
def home():
    try:   
        if request.method == 'POST':
            if current_user.is_authenticated:     
                print('---------------Communication with PIS to url-------------------')   
                #Create Transation token
                transaction_token = secrets.token_hex(16) 
                encoded_token = generate_password_hash( transaction_token, method='sha256')

                #Add to Database Transaction
                new_transaction = Transaction(price= session['total'] , token=encoded_token, user_id=current_user.id)
                db.session.add(new_transaction)
                db.session.commit()

                #Get user
                user = User.query.filter_by(id= current_user.id).first()

                # Get Nonce
                user_token = client_pb2.UserToken(token= encoded_token, merchantName="MerchantClothes")
                response = stub.getNonce(user_token) 
                print("-----------Get Nonce from PIS--------------")           

                #Encrypt Nonce with Symetric key of pis
                nonce_bytes = response.nonce.encode('utf-8')
                key = get_random_bytes(32)
                cipher = AES.new(key, AES.MODE_CFB)
                encryptedNonce = base64.b64encode(cipher.encrypt(nonce_bytes)).decode('utf-8')

                #Encrypt Symetric key of pis with publick key of pis
                sym_key = {
                    "key": base64.b64encode(key).decode('utf-8') ,
                    "iv": base64.b64encode(cipher.iv).decode('utf-8') 
                }
                sym_key_str = json.dumps(sym_key)  
                encryptedkey = encrypt_rsa(pis_cert, sym_key_str.encode("utf-8"))     
                
                #Sign with priv(hash(data))
                data = {
                    "name": user.name,
                    "email": user.email, 
                    "value": session['total'],
                    "store_name": "MerchantClothes",
                    "store_iban": "PT98765", 
                }

                data_str = json.dumps(data)
                data_bytes = data_str.encode('utf-8')
                digest = SHA256.new()
                digest.update(data_bytes)
                hashedData = sign_rsa(webserver_key, digest)
                
                #Sign with private key [hash(nonce + hash(data))]
                digest = SHA256.new()
                digest.update(nonce_bytes + hashedData.encode('utf-8'))  
                hashedNonce = sign_rsa(webserver_key, digest)

                #Encrypt data with Symetric key of bank
                key_bank = get_random_bytes(32)
                cipher = AES.new(key_bank, AES.MODE_CFB)
                encryptedData = base64.b64encode(cipher.encrypt(data_bytes)).decode('utf-8')

                #Encrypt Symetric key of bank
                sym_key_bank = {
                    "key": base64.b64encode(key_bank).decode('utf-8') ,
                    "iv": base64.b64encode(cipher.iv).decode('utf-8') 
                }
                key_str_bank = json.dumps(sym_key_bank)   
                encryptedkey_bank = encrypt_rsa(bank_cert, key_str_bank.encode("utf-8"))  
                    
                # Communicate with PIS
                msg_nonce = client_pb2.EncryptedNonce(hashedNonce = hashedNonce,
                                                    encryptedNonce = encryptedNonce,
                                                    encryptedKey =  encryptedkey)
                msg_data = client_pb2.EncryptedData( hashedData = hashedData,
                                                    encryptedData = encryptedData,
                                                    encryptedKey =  encryptedkey_bank)
                
                
                response = stub.requestURL(client_pb2.PaymentInfo(Nonce= msg_nonce, Data = msg_data, token = user_token)) 
                if response.url == "erro":
                    return render_template("error.html", user=current_user)

                session['url'] = response.url
                session['status'] = 0
                
                return render_template("payment.html", user= current_user, url = session['url'] )
            else:
                flash('You must Login to start the payment.', category='error')
        
        #Initiate user variables for website
        if 'total' not in session:
            init_session()
        
    except Exception as e:
        return render_template("error.html", user=current_user)
    
    return render_template("home.html", user= current_user, total = session['total'] , 
                            image1 = session['image1'] , image2 = session['image2'] , 
                            image3 = session['image3'], url = session['url'],
                            status = session['status'] )


@views.route('/admin', methods=['GET'])
@login_required
def admin():
    try:
        users = User.query.filter(User.username != "admin").all()
        users_length = len(users)
    except Exception as e:
        return render_template("error.html", user=current_user)

    return render_template("admin.html", user =current_user, users_length=users_length, users= users)


@views.route('/payment', methods=['GET','POST'])
def payment():
    print('---------------Redirect web browser for PIS-------------------') 
    return render_template("payment.html", user= current_user,status = session['status'], url = session["url"] )


@views.route('/select', methods=['POST'])
def select():
    try:
        value = json.loads(request.data)
        number = value['number']
        if number == 1:
            session['image1'] = not session['image1']
            if(session['image1']): 
                session['total'] += 40
            else:
                session['total'] -= 40
        elif number == 2:
            session['image2'] = not session['image2']
            if(session['image2']): 
                session['total'] += 50
            else:
                session['total'] -= 50
        elif number == 3: 
            session['image3'] = not session['image3']
            if(session['image3']): 
                session['total'] += 70
            else:
                session['total'] -= 70
    
    except Exception as e:
        return jsonify(erro = 1)    #Error occured

    return jsonify(erro = 0)


@views.route('/deletedb', methods=['POST'])
def deletedb():    
    try:
        User.query.filter(User.username != "admin").delete() 
        Transaction.query.delete() 
        db.session.commit()
        print('---------------Database was deleted-------------------') 

    
    except Exception as e:
        return jsonify(erro = 1)    #Error occured

    return jsonify(erro = 0)
    

@views.route('/status', methods=['GET','POST'])
def status():
    try:
        print('---------------Checking status of Transaction with PIS-------------------') 
        encoded_token = Transaction.query.filter(Transaction.user_id == current_user.id).all()[-1].token
        response = stub.requestConfirmation(client_pb2.UserToken(token= encoded_token, merchantName="MerchantClothes" )) 

        if response.status == "confirmed":
            session['status'] = 3
        elif response.status == "pending":
            session['status'] = 2
        elif response.status == "cancelled":   
            session['status'] = 1  

    except Exception as e:
        return jsonify(erro = 1)    #Error occured

    return jsonify(erro = 0)

@views.route('/error', methods=['GET','POST'])
def error():
    return render_template("error.html", user= current_user)

def encrypt_rsa(key, data):
    signer = PKCS1_OAEP.new(key)
    data_encrypted = signer.encrypt(data)
    return base64.b64encode(data_encrypted).decode('utf-8')

def sign_rsa(key, data):
    signer = pkcs1_15.new(key)
    data_encrypted = signer.sign(data)
    return base64.b64encode(data_encrypted).decode('utf-8')

def init_session():
    session['total'] = 0.0
    session['image1'] = False
    session['image2'] = False
    session['image3'] = False
    session['url'] = None
    session['status'] = 0
    pass