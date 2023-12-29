import string
import random
import json

from flask import (
    session,
)

import requests

from pokemon.database import get_db

cache = {}


def create(length_of_id):
    game_id = "".join(
        random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)
        for _ in range(length_of_id)
    )
    guess = reset_guess("")
    life = reset_life(7)
    pokemon_id = reset_pokemon(0)
    score = reset_score(0)
    streak = reset_streak(0)
    print(f"{pokemon_id = }")
    if pokemon_id:
        db = get_db()
        db.execute(
            "INSERT INTO game (game_id, guess, life, pokemon_id, score, streak) VALUES (?, ?, ?, ?, ?, ?)",
            (game_id, guess, life, pokemon_id, score, streak),
        )
        db.commit()
    return game_id


def fetch_pokemon(id):
    url = f"http://localhost:8000/api/pokemon/{id}"
    res = requests.get(url)
    return json.loads(res.content)


def get_guess(name):
    return " ".join(
        [
            x
            if x in (session.get("guess_exclude") + session.get("guess_player"))
            else "_"
            for x in name
        ]
    )


def load_game(_id):
    db = get_db()
    game = db.execute(
        "SELECT guess, life, pokemon_id, score, streak FROM game WHERE game_id=?",
        (_id,),
    ).fetchone()
    if game:
        reset_guess(game["guess"])
        reset_life(game["life"])
        reset_pokemon(game["pokemon_id"])
        reset_score(game["score"])
        reset_streak(game["streak"])
        return True
    return False


def load_next_pokemon():
    del session["pokemon"]
    reset_guess("")
    reset_life(7)
    reset_pokemon(0)
    session["score"] += 100 + session["streak"] * 10
    session["streak"] += 1


def load_pokemon():
    _id = session.get("pokemon").get("id")
    print(f"{_id = }")
    # 787 TAPU BULU
    if not _id in cache:
        pokemon = fetch_pokemon(_id)
        cache[_id] = pokemon
    return cache[_id]


def reset_guess(guess):
    session["guess_exclude"] = "2'. -"
    session["guess_player"] = guess
    return guess


def reset_life(life):
    session["life"] = life
    return life


def reset_pokemon(_id):
    if not _id:
        _id = random.choice(range(899))
    session["pokemon"] = {"id": _id}
    return _id


def reset_score(score):
    session["score"] = score
    return score


def reset_streak(streak):
    session["streak"] = streak
    return streak


def save_game(game_id):
    db = get_db()
    sql = """ UPDATE game 
            SET guess = ?,
                life = ?, 
                pokemon_id = ?,
                score = ?,
                streak = ?
            WHERE game_id = ?"""
    db.execute(
        sql,
        (
            session["guess_player"],
            session["life"],
            session["pokemon"]["id"],
            session["score"],
            session["streak"],
            game_id,
        ),
    )
    db.commit()
