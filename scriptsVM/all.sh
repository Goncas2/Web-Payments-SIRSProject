#!/bin/bash

sudo apt-get -y update
sudo apt-get -y install python3

sudo apt-get -y update
sudo apt-get -y install python3-pip

pip3 install grpcio
pip3 install grpcio-tools
pip3 install flask
pip3 install pycryptodome


