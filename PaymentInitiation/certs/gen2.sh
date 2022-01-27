

# 1. Generate PIS's private key and certificate signing request (CSR)
openssl req -newkey rsa:4096 -nodes -keyout pis-key.pem -out pis-req.pem -subj "/C=PT/ST=Lisbon/L=Lisbon/O=Instituto Superior Tecnico/OU=Computer/CN=192.168.56.11/emailAddress=pis@gmail.com" -addext "subjectAltName=DNS:192.168.56.11,IP:192.168.56.11"

# 2. Use CA's private key to sign PIS's CSR and get back the signed certificate
openssl x509 -req -in pis-req.pem -days 60 -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out pis-cert.pem -extfile pis-ext.cnf



# 3. Generate webserver's private key and certificate signing request (CSR)
openssl req -newkey rsa:4096 -nodes -keyout webserver-key.pem -out webserver-req.pem -subj "/C=PT/ST=Lisbon/L=Lisbon/O=Instituto Superior Tecnico/OU=Computer/CN=192.168.56.10/emailAddress=webserver@gmail.com" -addext "subjectAltName=DNS:192.168.56.10,IP:192.168.56.10"

# 4. Use CA's private key to sign webserver's CSR and get back the signed certificate
openssl x509 -req -in webserver-req.pem -days 365 -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out webserver-cert.pem -extfile webserver-ext.cnf

# 5. Generate bank's private key and certificate signing request (CSR)
openssl req -newkey rsa:4096 -nodes -keyout bank-key.pem -out bank-req.pem -subj "/C=PT/ST=Lisbon/L=Lisbon/O=Instituto Superior Tecnico/OU=Computer/CN=192.168.56.12/emailAddress=webserver@gmail.com" -addext "subjectAltName=DNS:192.168.56.12,IP:192.168.56.12"

# 6. Use CA's private key to sign bank's CSR and get back the signed certificate
openssl x509 -req -in bank-req.pem -days 365 -CA ca-cert.pem -CAkey ca-key.pem -CAcreateserial -out bank-cert.pem -extfile bank-ext.cnf