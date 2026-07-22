import os

from flask import current_app

from pokemon.database import get_db


def create_game(pokedex_number, user_id=None):
    """Insert a new game row for the given starting Pokemon and return its game_id."""
    game_id = os.urandom(10).hex()
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO game (game_id, guessed_letters, lives, pokedex_number, score, streak, user_id) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (game_id, "", 7, pokedex_number, 0, 0, user_id),
    )
    db.commit()
    return game_id


def get_game(game_id):
    """Fetch a single game row by game_id, or None if it doesn't exist."""
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM game WHERE game_id = %s", (game_id,))
    return cur.fetchone()


def save_game(game):
    """Persist the current in-memory game state back to the database."""
    db = get_db()
    cur = db.cursor()
    current_app.logger.debug(f"save_game, game = {game}")
    cur.execute(
        """UPDATE game
             SET guessed_letters = %s,
                 lives = %s,
                 player = %s,
                 pokedex_number = %s,
                 score = %s,
                 streak = %s,
                 user_id = %s
             WHERE game_id = %s""",
        (
            game["guessed_letters"],
            game["lives"],
            game.get("player"),
            game["pokedex_number"],
            game["score"],
            game["streak"],
            game.get("user_id"),
            game["game_id"],
        ),
    )
    db.commit()
    return get_game(game["game_id"])


def get_games_by_score():
    """Top 10 players by their best score.

    Each player appears at most once — their highest score is used.
    For logged-in users the current display_name from app_user is shown,
    so renames are reflected immediately. Guest scores use the player text
    saved on the game row.
    """
    db = get_db()
    cur = db.cursor()
    cur.execute(
        """SELECT
               COALESCE(u.display_name, g.player) AS player,
               MAX(g.score) AS score
           FROM game g
           LEFT JOIN app_user u ON u.user_id = g.user_id
           WHERE (g.player IS NOT NULL OR g.user_id IS NOT NULL)
             AND g.score != 0
           GROUP BY COALESCE(u.display_name, g.player)
           ORDER BY score DESC
           LIMIT 10"""
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
