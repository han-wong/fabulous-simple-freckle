#!/bin/bash

# For development use (simple logging, etc):
python fabulous-simple-freckle/server.py

# For production use: 
# gunicorn --chdir fabulous-simple-freckle server:app -w 1 --log-file -