from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)
    token = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
 
    