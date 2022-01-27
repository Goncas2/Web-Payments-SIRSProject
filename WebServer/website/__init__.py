from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import secrets
from werkzeug.security import generate_password_hash
import client_pb2_grpc
import grpc
from Crypto.PublicKey import RSA

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secrets.token_bytes(32)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    # Flask-SQLAlchemy's event system disable to save resources
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
    app.config.update(SESSION_COOKIE_NAME='MERCHANT')
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    create_database(app)
    populate_db(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app


def create_database(app):
    db.create_all(app=app)
    print('--------------------Created Database!-----------------------')


def init_stub():
    with open("certs/webserver-key.pem", "r") as src:
        webserver_key = RSA.importKey(src.read(), passphrase="testwebserver")
        decrypted_key = webserver_key.export_key("PEM",None,pkcs=1)
        
    with open('certs/ca-cert.pem', 'rb') as f:
                ca_cert = f.read()

    with open('certs/webserver-cert.pem', 'rb') as f:
                webserver_cert = f.read()

    #Create Channel and Stub            
    creds = grpc.ssl_channel_credentials(certificate_chain=webserver_cert, private_key=decrypted_key, root_certificates=ca_cert)
    channel = grpc.secure_channel("192.168.56.11:4001", creds)
    
    stub = client_pb2_grpc.PIServiceStub(channel)
    return stub

def populate_db(app):
    from .models import User
    #add Admin to DB
    app.app_context().push()
    with app.app_context():
        admin = User.query.filter(User.username == "admin").first()

        if admin is None:
            #Add Salt
            salt = secrets.token_hex(32)
            password = "ola12345admin" + salt    
            hash = generate_password_hash(password, method='sha256') + salt

            #Add Admin to DB
            new_user = User(username="admin", email="admin@gmail.com", name="administrator", password=hash) 
            db.session.add(new_user)
            db.session.commit()