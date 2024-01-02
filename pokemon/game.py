import os
import string
import random
import json

from flask import (
    current_app,
    session,
)

import requests

from pokemon.database import get_db

EXCLUDE_IN_GUESS = "2'. -"
cache = {}


def create(length_of_id):
    session["game_id"] = os.urandom(length_of_id).hex()
    session["guess"] = ""
    load_hi_score()
    session["life"] = 7
    session["player"] = None
    reset_pokemon(0)
    session["score"] = 0
    session["streak"] = 0
    if session["pokemon_id"]:
        db = get_db()
        db.execute(
            "INSERT INTO game (game_id, guess, life, pokemon_id, score, streak) VALUES (?, ?, ?, ?, ?, ?)",
            (
                session["game_id"],
                session["guess"],
                session["life"],
                session["pokemon_id"],
                session["score"],
                session["streak"],
            ),
        )
        db.commit()
    return session["game_id"]


def fetch_pokemon(id):
    url = current_app.config["POKEMON"] + id
    res = requests.get(url)
    return json.loads(res.content)


def get_current_word(name):
    current_word = " ".join(
        [x if x in (EXCLUDE_IN_GUESS + session["guess"]) else "_" for x in name]
    )
    current_app.logger.debug(f"current_word = {current_word}")
    return current_word


def get_games_by_score():
    db = get_db()
    return db.execute(
        "SELECT player, score FROM game WHERE player IS NOT NULL AND score !=0 ORDER BY score DESC LIMIT 10;"
    ).fetchall()


def load_hi_score():
    db = get_db()
    (score,) = db.execute("SELECT max(score) FROM game;").fetchone()
    session["hi_score"] = score if score else 0


def load_game(_id):
    db = get_db()
    game = db.execute(
        "SELECT * FROM game WHERE game_id = ? AND player IS NULL",
        (_id,),
    ).fetchone()
    current_app.logger.debug(f"load_game, session = {session}")
    if game:
        session["guess"] = game["guess"]
        session["life"] = game["life"]
        session["player"] = game["player"]
        reset_pokemon(game["pokemon_id"])
        session["score"] = game["score"]
        session["streak"] = game["streak"]
        load_hi_score()
        return True
    return False


def load_next_pokemon():
    session["guess"] = ""
    session["life"] = 7
    reset_pokemon(0)
    session["score"] += 100 + session["streak"] * 10
    session["streak"] += 1
    current_app.logger.debug(f"load_next_pokemon, session = {session}")


def load_pokemon():
    _id = session["pokemon_id"]
    print(f"_id = {_id}")
    # 787 TAPU BULU
    if not _id in cache:
        pokemon = fetch_pokemon(_id)
        cache[_id] = pokemon
    return cache[_id]


def reset_pokemon(_id):
    if not _id:
        _id = random.choice(range(899))
    session["pokemon_id"] = _id
    return _id


def save_game(game_id):
    db = get_db()
    sql = """ UPDATE game 
            SET guess = ?,
                life = ?, 
                player = ?,
                pokemon_id = ?,
                score = ?,
                streak = ?
            WHERE game_id = ?"""
    db.execute(
        sql,
        (
            session["guess"],
            session["life"],
            session["player"],
            session["pokemon_id"],
            session["score"],
            session["streak"],
            game_id,
        ),
    )
    db.commit()
