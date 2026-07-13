#!/bin/bash

# For development use (simple logging, etc):
# python3 -m pip install -r requirements.txt
# flask --app pokemon run --debug

# For production use:
python3 -m gunicorn "pokemon:create_app()" -w 1 --log-file - --bind 0.0.0.0:$PORT