import json
import requests
from flask import current_app

cache = {}


def fetch_pokemon_from_api(pokedex_number):
    """Call the Pokemon image API directly (no cache). Returns raw parsed JSON."""
    url = current_app.config["POKEMON_API_URL"] + str(pokedex_number)
    res = requests.get(url)
    return json.loads(res.content)


def get_pokemon(pokedex_number):
    """Cached lookup of a Pokemon's name/original/silhouette data."""
    if pokedex_number not in cache:
        pokemon = fetch_pokemon_from_api(pokedex_number)
        pokemon["name"] = pokemon["name"].upper()
        cache[pokedex_number] = pokemon
    return cache[pokedex_number]
