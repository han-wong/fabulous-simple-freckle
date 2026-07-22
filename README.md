# Pokemon Hangman (Flask)

A hangman game where you guess Pokemon names, with a persistent hi-scores leaderboard.

## Dependencies

This app calls a separate Pokemon image API service (`stone-cedar-potassium`) to fetch
sprites and generate silhouettes. That service must be deployed/running and reachable
via the `FLASK_POKEMON` env var before this app will work correctly.

## Create a virtual environment
- `python -m venv venv`
- `.\venv\Scripts\activate`

## Install dependencies
- `python -m pip install -r requirements.txt`

## Environment variables

Create a `.env` file in the project root with:

```
FLASK_ENVIRONMENT=Development
FLASK_DATABASE_URL=<your Supabase Postgres connection string>
FLASK_POKEMON=<url of the deployed pokemon-api service, e.g. https://pokemon-api.onrender.com/api/pokemon/>
FLASK_SECRET_KEY=<any random string, used for sessions>
FLASK_SUPABASE_URL=<your Supabase project URL>
FLASK_SUPABASE_ANON_KEY=<your Supabase anon/public key>
```

## Initialize git (for a fresh clone pointing at the existing GitHub repo)
- `git init`
- `git branch -m main`
- `git remote add origin git@github.com:han-wong/fabulous-simple-freckle.git`
- `git fetch origin`
- `git branch --set-upstream-to=origin/main main`
- `git reset --hard origin/main`

## Initialize or reset the database

The database schema is created automatically on app startup, but you can also
trigger it manually:
- `python -m flask --app pokemon init-db`

## Clean up old, unfinished games (optional maintenance)
- `python -m flask --app pokemon prune-games` (deletes unfinished games older than 7 days)
- `python -m flask --app pokemon prune-games --days 14` (custom window)

## For development use (auto-reload, debug pages):
- `python -m flask --app pokemon run --debug`

## For production use:
- `python -m gunicorn "pokemon:create_app()" -w 1 --log-file - --bind 0.0.0.0:$PORT`