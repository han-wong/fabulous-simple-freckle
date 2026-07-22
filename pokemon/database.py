import os
import psycopg2
import psycopg2.extras
import click
from flask import current_app, g

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(prune_games_command)

    with app.app_context():
        _ensure_db()

@click.command("init-db")
def init_db_command():
    _ensure_db()
    click.echo("You successfully initialized the database!")

@click.command("prune-games")
@click.option("--days", default=7, help="Delete unfinished games older than this many days.")
def prune_games_command(days):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "DELETE FROM game WHERE player IS NULL AND created < NOW() - INTERVAL %s",
        (f"{days} days",),
    )
    deleted = cur.rowcount
    db.commit()
    click.echo(f"Pruned {deleted} unfinished game(s) older than {days} day(s).")

DEFAULT_HI_SCORES = [
    ("Han",     850),
    ("Ash",     720),
    ("Misty",   610),
    ("Brock",   540),
    ("Gary",    430),
]

def _ensure_db():
    """Create tables if they don't exist yet and seed default hi-scores. Safe to call on every startup."""
    db = get_db()
    cur = db.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS game (
            id SERIAL PRIMARY KEY,
            created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            game_id TEXT NOT NULL,
            guessed_letters TEXT NOT NULL,
            lives INTEGER NOT NULL,
            player TEXT,
            user_id TEXT,
            pokedex_number TEXT NOT NULL,
            score INTEGER NOT NULL,
            streak INTEGER NOT NULL
        )"""
    )
    # Add user_id to tables that predate this column
    cur.execute("ALTER TABLE game ADD COLUMN IF NOT EXISTS user_id TEXT")
    cur.execute(
        """CREATE TABLE IF NOT EXISTS app_user (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL UNIQUE,
            created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS pokemon_stats (
            pokedex_number TEXT PRIMARY KEY,
            solved INTEGER NOT NULL DEFAULT 0,
            failed INTEGER NOT NULL DEFAULT 0
        )"""
    )
    db.commit()
    _seed_default_scores(db)

def _seed_default_scores(db):
    """Insert default hi-score entries only if no real scores exist yet."""
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) FROM game WHERE player IS NOT NULL")
    row = cur.fetchone()
    count = row["count"]
    current_app.logger.debug(f"_seed_default_scores: existing named games = {count}")
    if count == 0:
        for player, score in DEFAULT_HI_SCORES:
            cur.execute(
                "INSERT INTO game (game_id, guessed_letters, lives, player, pokedex_number, score, streak) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (os.urandom(10).hex(), "", 0, player, "1", score, 0),
            )
        db.commit()
        current_app.logger.debug("_seed_default_scores: inserted 5 default hi-scores")
    else:
        current_app.logger.debug("_seed_default_scores: skipped, real scores already exist")

def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(
            current_app.config["DATABASE_URL"],
            cursor_factory=psycopg2.extras.RealDictCursor,
        )
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()