rm *.pem

# 1. Generate CA's private key and self-signed certificate
openssl req -x509 -newkey rsa:4096 -days 365 -keyout certs/ca-key.pem -out certs/ca-cert.pem -subj "/C=PT/ST=Lisbon/L=Lisbon/O=Instituto Superior Tecnico/OU=Education/CN=localhost/emailAddress=certificate.authority@tecnico.ulisboa.pt"

# 2. Generate web server's private key and certificate signing request (CSR)
openssl req -newkey rsa:4096 -keyout certs/webserver-key.pem -out certs/webserver-req.pem -subj "/C=PT/ST=Lisbon/L=Lisbon/O=Instituto Superior Tecnico/OU=Computer/CN=192.168.56.11/emailAddress=webserver@gmail.com" 

# 3. Use CA's private key to sign web server's CSR and get back the signed certificate
openssl x509 -req -in certs/webserver-req.pem -days 365 -CA certs/ca-cert.pem -CAkey certs/ca-key.pem -CAcreateserial -out certs/webserver-cert.pem -extfile certs/webserver-ext.cnf

# 4. Generate PIS's private key and certificate signing request (CSR)
openssl req -newkey rsa:4096 -keyout certs/pis-key.pem -out certs/pis-req.pem -subj "/C=PT/ST=Lisbon/L=Lisbon/O=Instituto Superior Tecnico/OU=Computer/CN=192.168.56.10/emailAddress=pis@gmail.com" 

# 5. Use CA's private key to sign PIS's CSR and get back the signed certificate
openssl x509 -req -in certs/pis-req.pem -days 60 -CA certs/ca-cert.pem -CAkey certs/ca-key.pem -CAcreateserial -out certs/pis-cert.pem -extfile certs/pis-ext.cnf

# 6. Generate Bank's private key and certificate signing request (CSR)
openssl req -newkey rsa:4096 -keyout certs/bank-key.pem -out certs/bank-req.pem -subj "/C=PT/ST=Lisbon/L=Lisbon/O=Instituto Superior Tecnico/OU=Computer/CN=192.168.56.12/emailAddress=pis@gmail.com"

# 7. Use CA's private key to sign bank's CSR and get back the signed certificate
openssl x509 -req -in certs/bank-req.pem -days 60 -CA certs/ca-cert.pem -CAkey certs/ca-key.pem -CAcreateserial -out certs/bank-cert.pem -extfile certs/bank-ext.cnf

#Keys of Merchant Server
rm WebServer/certs/*.pem
cp certs/webserver-cert.pem certs/webserver-key.pem certs/pis-cert.pem certs/bank-cert.pem certs/ca-cert.pem WebServer/certs

#Keys of PIS
rm PaymentInitiation/certs/*.pem
cp certs/pis-cert.pem certs/pis-key.pem certs/webserver-cert.pem certs/bank-cert.pem certs/ca-cert.pem PaymentInitiation/certs

#Keys of Bank
rm Bank/certs/*.pem
cp certs/bank-cert.pem certs/bank-key.pem certs/webserver-cert.pem certs/pis-cert.pem certs/ca-cert.pem Bank/certs