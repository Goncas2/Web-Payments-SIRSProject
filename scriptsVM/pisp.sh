pip install flask
pip install flask-login

cd /home/vagrant/PaymentInitiation

python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./protos/bank.proto
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./backend/server.proto
