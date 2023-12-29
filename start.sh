#!/bin/bash

# For development use (simple logging, etc):
# python3 -m pip install -r requirements.txt
# python3 server.py

# For production use: 
python3 -m gunicorn pokemon:app -w 1 --log-file -