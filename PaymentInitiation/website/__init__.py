import secrets
from flask import Flask, session
import sqlite3
from sqlite3 import Error
from protos import bank_pb2_grpc
import grpc
from Crypto.PublicKey import RSA


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secrets.token_bytes(32)
    app.config.update(SESSION_COOKIE_NAME='PISP')

    from .views import views
    
    app.register_blueprint(views, url_prefix='/')
    return app

def connect_db(path):
    try:
        return sqlite3.connect(path)
    except Error as e:
        print(e)
        
def init_stub():
    with open('certs/ca-cert.pem', 'rb') as f:
                ca_cert = f.read()
    with open("certs/pis-key.pem", "r") as src:
        pis_key = RSA.importKey(src.read(), passphrase="testpis")
        decrypted_key = pis_key.export_key("PEM",None,pkcs=1)
    with open('certs/pis-cert.pem', 'rb') as f:
                pis_cert = f.read()

    #Create Channel and Stub            
    creds = grpc.ssl_channel_credentials(certificate_chain=pis_cert, private_key=decrypted_key, root_certificates=ca_cert)
    channel = grpc.secure_channel("192.168.56.12:2001", creds)
    
    stub = bank_pb2_grpc.bankStub(channel)
    return stub

