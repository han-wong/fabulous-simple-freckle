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

def _ensure_db():
    """Create tables if they don't exist yet. Safe to call on every startup."""
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