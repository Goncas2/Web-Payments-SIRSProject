#!/bin/bash

pip3 install flask-login
pip3 install flask-sqlalchemy

cd /home/vagrant/WebServer
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. ./client.proto
