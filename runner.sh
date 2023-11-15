#!/bin/bash
python3 -m pip install --upgrade pip
python3 -m pip install virtualenv
python3 -m virtualenv env
source env/bin/activate
pip3 install -r requirements.txt
python3 server.py & python3 client.py