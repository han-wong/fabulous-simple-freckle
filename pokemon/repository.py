import os
from flask import current_app
from pokemon.database import get_db


def create_game(pokedex_number):
    """Insert a new game row for the given starting Pokemon and return its game_id."""
    game_id = os.urandom(10).hex()
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO game (game_id, guessed_letters, lives, pokedex_number, score, streak) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (game_id, "", 7, pokedex_number, 0, 0),
    )
    db.commit()
    return game_id


def select_game(game_id):
    """Fetch a single game row by game_id, or None if it doesn't exist."""
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT * FROM game WHERE game_id = %s",
        (game_id,),
    )
    return cur.fetchone()


def save_game(game):
    """Persist the current in-memory game state back to the database."""
    db = get_db()
    cur = db.cursor()
    current_app.logger.debug(f"save_game, game = {game}")
    sql = """UPDATE game
             SET guessed_letters = %s,
                 lives = %s,
                 player = %s,
                 pokedex_number = %s,
                 score = %s,
                 streak = %s
             WHERE game_id = %s"""
    cur.execute(
        sql,
        (
            game["guessed_letters"],
            game["lives"],
            game["player"],
            game["pokedex_number"],
            game["score"],
            game["streak"],
            game["game_id"],
        ),
    )
    db.commit()
    return select_game(game["game_id"])


def get_games_by_score():
    """Top 10 named, scoring games — used for the hi-scores leaderboard."""
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT player, score FROM game "
        "WHERE player IS NOT NULL AND score != 0 "
        "ORDER BY score DESC LIMIT 10"
    )
    return cur.fetchall()


def get_hi_score():
    """The single highest score across all games, or 0 if none yet."""
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT max(score) FROM game;")
    row = cur.fetchone()
    score = row["max"] if row else None
    return score if score else 0
