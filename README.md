# Python Flask project

## Create a virtual environment
- python -m venv venv
- .\venv\Scripts\activate

## Install django 
- python3 -m pip install -r requirements.txt

## Initialize git
- git init
- git branch -m main
- git remote add origin git@github.com:han-wong/buttered-oil-vacation.git
- git fetch origin
- git branch --set-upstream-to=origin/main main
- git reset --hard origin/main
- git reset --hard HEAD

## Initialize database or reset
- python3 -m flask --app pokemon init-db

## For development use (simple logging, etc):
- python3 -m flask --app board run --port 8000 --debug

## For production use: 
- python3 -m gunicorn "board:create_app()" -w 1 --log-file -