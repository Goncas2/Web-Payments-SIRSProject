import grpc
from website import create_app
from backend import server
from threading import Thread
from backend import connectSql
import ssl

app = create_app()

if __name__ == '__main__':

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain( 'certs/bank-cert.pem', keyfile = 'certs/bank-key.pem', password="testbank")

    thread = Thread(target = app.run, kwargs={"host":"0.0.0.0", "port":"443", "ssl_context":context })
    thread.daemon = True
    thread.start()

    connectSql.cleanDb()
    connectSql.createDb()

    connectSql.insertInitialValuesDb()

    server.serve()
