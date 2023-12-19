#!/bin/bash

cd fabulous-simple-freckle

# For development use (simple logging, etc):
# python3 -m pip install -r requirements.txt
# python3 server.py

# For production use: 
gunicorn server:app -w 1 --log-file -