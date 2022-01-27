import secrets
import ssl
from website import create_app
from backend import server
from threading import Thread
import sqlite3
from sqlite3 import Error
from db import initdb
from werkzeug.security import generate_password_hash


app = create_app()

def create_database(db):
    c = db.cursor()
    
    c.execute(initdb.drop_transactions_table_sql)
    c.execute(initdb.drop_nonces_table_sql)
    c.execute(initdb.drop_accounts_table_sql)
    
    c.execute(initdb.create_transactions_table_sql)
    c.execute(initdb.create_nonces_table_sql)
    c.execute(initdb.create_accounts_table_sql)
    
    salt = secrets.token_hex(32)
    password = "sirsisnice123" + salt    
    hash1 = generate_password_hash(password, method='sha256') + salt
    c.execute(initdb.add_user, ("sirs.client.tester2.08@gmail.com", hash1, "PT12345"))
    
    salt = secrets.token_hex(32)
    password = "sirsisnice123" + salt    
    hash2 = generate_password_hash(password, method='sha256') + salt
    c.execute(initdb.add_user, ("sirs.client.tester.08@gmail.com", hash2, "PT1234"))
    
    db.commit()


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        create_database(conn)
        print("---------------Database Created---------------")
    except Error as e:
        print(e)


if __name__ == '__main__':
        
    create_connection("db/pisp.sqlite")
    
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain( 'certs/pis-cert.pem', keyfile = 'certs/pis-key.pem', password="testpis")
    
    thread = Thread(target = app.run, kwargs={"host":"192.168.56.11", "port":"443", "ssl_context":context})
    thread.daemon = True
    thread.start()
    
    server.serve()
     