import json
import os
import random
import requests

from flask import current_app
from pokemon.database import get_db

EXCLUDE_IN_GUESS = "2♀♂'. -"
MAX_POKEMON_NUMBER = 899
cache = {}


def create_game():
    game_id = os.urandom(10).hex()
    db = get_db()
    db.execute(
        "INSERT INTO game (game_id, guess, life, pokemon_id, score, streak) VALUES (?, ?, ?, ?, ?, ?)",
        (game_id, "", 7, random.randrange(32, MAX_POKEMON_NUMBER), 0, 0,),
        # (game_id, "", 7, 669, 0, 0,), # FLABÉBÉ
    )
    db.commit()
    return game_id


def fetch_pokemon(id):
    url = current_app.config["POKEMON"] + str(id)
    res = requests.get(url)
    return json.loads(res.content)


def handle_guess(game, guess):
    guess = guess.upper()
    if game["life"] > 0 and "_" in game["current_word"]:
        pokemon = get_pokemon(game["pokemon_id"])
        name = pokemon["name"]

        if guess == "E" and "É" in name:
            pass
        elif guess not in name:
            game["life"] -= 1
            game["streak"] = 0

        game["guess"] += guess
        save_game(game)
    return get_game(game["game_id"])


def get_current_word(game):
    pokemon = get_pokemon(game["pokemon_id"])
    current_app.logger.debug(
        f'get_current_word, pokemon["name"] = {pokemon["name"]}')
    return " ".join([
        x if x in (EXCLUDE_IN_GUESS + game["guess"]) else
        "É" if x == "É" and "E" in game["guess"] else
        "_" for x in pokemon["name"]
    ])


def get_game(game_id):
    game = select_game(game_id)
    if game:
        game = dict(game)
        game["current_word"] = get_current_word(game)
        return game


def get_pokemon(pokemon_id):
    if not pokemon_id in cache:
        pokemon = fetch_pokemon(pokemon_id)
        pokemon["name"] = pokemon['name'].upper()
        cache[pokemon_id] = pokemon
    return cache[pokemon_id]


def get_game_state(game):
    pokemon = get_pokemon(game["pokemon_id"])
    image = pokemon["original"]
    message = "It's {}!".format(pokemon["name"])

    current_app.logger.debug(f"get_game_state, name = {pokemon['name']}")

    if "_" in game["current_word"] and game["life"]:
        image = pokemon["silhouette"]
        message = "Who's That Pokémon?"
    elif game["life"]:
        load_next_pokemon(game)
    else:
        save_game(game)

    return (message, get_hi_score(), image)


def get_games_by_score():
    db = get_db()
    return db.execute(
        "SELECT player, score FROM game WHERE player IS NOT NULL AND score !=0 ORDER BY score DESC LIMIT 10"
    ).fetchall()


def get_hi_score():
    db = get_db()
    (score,) = db.execute("SELECT max(score) FROM game;").fetchone()
    return score if score else 0


def load_next_pokemon(game):
    game["guess"] = ""
    game["life"] = 7
    game["pokemon_id"] = random.randrange(1, MAX_POKEMON_NUMBER)
    game["score"] += 100 + game["streak"] * 10
    game["streak"] += 1
    return save_game(game)


def save_game(game):
    db = get_db()
    current_app.logger.debug(f"save_game, game = {game}")

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
            game["guess"],
            game["life"],
            game["player"],
            game["pokemon_id"],
            game["score"],
            game["streak"],
            game["game_id"],
        ),
    )
    db.commit()
    return get_game(game["game_id"])


def select_game(game_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM game WHERE game_id = ?",
        (game_id,),
    ).fetchone()
