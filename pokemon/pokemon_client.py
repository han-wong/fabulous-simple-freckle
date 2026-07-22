import json
import requests
from flask import current_app

cache = {}


def fetch_pokemon_from_api(pokedex_number):
    """Call the Pokemon image API directly (no cache). Returns raw parsed JSON."""
    url = current_app.config["POKEMON_API_URL"] + str(pokedex_number)
    try:
        res = requests.get(url, timeout=60)
    except requests.exceptions.RequestException as e:
        current_app.logger.error(
            f"fetch_pokemon_from_api: request to {url} failed: {e}")
        raise

    current_app.logger.debug(
        f"fetch_pokemon_from_api: GET {url} -> status {res.status_code}, "
        f"{len(res.content)} bytes"
    )

    try:
        return json.loads(res.content)
    except json.JSONDecodeError:
        current_app.logger.error(
            f"fetch_pokemon_from_api: non-JSON response from {url} "
            f"(status {res.status_code}): {res.content[:300]!r}"
        )
        raise


def get_pokemon(pokedex_number):
    """Cached lookup of a Pokemon's name/original/silhouette data."""
    if pokedex_number not in cache:
        pokemon = fetch_pokemon_from_api(pokedex_number)
        pokemon["name"] = pokemon["name"].upper()
        cache[pokedex_number] = pokemon
    return cache[pokedex_number]
