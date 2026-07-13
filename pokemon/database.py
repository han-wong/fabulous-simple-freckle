import sqlite3
import click
from flask import current_app, g

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

    with app.app_context():
        _ensure_db()

@click.command("init-db")
def init_db_command():
    _init_db()
    click.echo("You successfully initialized the database!")

def _init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))

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
    db.execute(
        """CREATE TABLE IF NOT EXISTS game (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            game_id TEXT NOT NULL,
            guess TEXT NOT NULL,
            life INTEGER NOT NULL,
            player TEXT,
            pokemon_id TEXT NOT NULL,
            score INTEGER NOT NULL,
            streak INTEGER NOT NULL
        )"""
    )
    db.commit()
    _seed_default_scores(db)

def _seed_default_scores(db):
    """Insert default hi-score entries if the table is empty."""
    (count,) = db.execute("SELECT COUNT(*) FROM game WHERE player IS NOT NULL").fetchone()
    if count == 0:
        import os
        for player, score in DEFAULT_HI_SCORES:
            db.execute(
                "INSERT INTO game (game_id, guess, life, player, pokemon_id, score, streak) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (os.urandom(10).hex(), "", 0, player, "1", score, 0),
            )
        db.commit()

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()