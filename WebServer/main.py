from website import create_app
import ssl 
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain( 'certs/webserver-cert.pem', keyfile = 'certs/webserver-key.pem', password="testwebserver")

app = create_app()


if __name__ == '__main__':
    app.run(host="192.168.56.10", port="443", debug=True, ssl_context= context)
    