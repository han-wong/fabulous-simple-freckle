import random
from flask import current_app
from pokemon import repository
from pokemon import pokemon_client

EXCLUDE_IN_GUESS = "2♀♂'. -"
MAX_POKEMON_NUMBER = 899


def start_new_game():
    """Pick a random starting Pokemon and create a fresh game. Returns the new game_id."""
    starting_pokemon = random.randrange(32, MAX_POKEMON_NUMBER)
    return repository.create_game(starting_pokemon)


def get_game(game_id):
    """Fetch a game row and enrich it with the current masked display word."""
    game = repository.select_game(game_id)
    if game:
        game = dict(game)
        game["masked_name"] = get_masked_name(game)
        return game


def get_masked_name(game):
    """Build the partially-revealed Pokemon name, e.g. 'P _ _ H A _ H U'."""
    pokemon = pokemon_client.get_pokemon(game["pokedex_number"])
    current_app.logger.debug(
        f'get_masked_name, pokemon["name"] = {pokemon["name"]}')
    return " ".join([
        letter if letter in (EXCLUDE_IN_GUESS + game["guessed_letters"]) else
        "É" if letter == "É" and "E" in game["guessed_letters"] else
        "_" for letter in pokemon["name"]
    ])


def handle_guess(game, letters):
    """Apply one or more new guessed letters in order, updating lives/streak/guessed_letters.
    Stops early if lives run out mid-batch. Writes to the database once, after the whole batch."""
    pokemon = pokemon_client.get_pokemon(game["pokedex_number"])
    name = pokemon["name"]
    changed = False

    for letter in letters.upper():
        if game["lives"] <= 0 or "_" not in game["masked_name"]:
            break
        if letter == "E" and "É" in name:
            pass
        elif letter not in name:
            game["lives"] -= 1
            game["streak"] = 0
        game["guessed_letters"] += letter
        game["masked_name"] = get_masked_name(game)
        changed = True

    if changed:
        repository.save_game(game)
    return get_game(game["game_id"])


def load_next_pokemon(game):
    """Round was won: award points, bump the streak, and move to a new Pokemon."""
    game["guessed_letters"] = ""
    game["lives"] = 7
    game["pokedex_number"] = random.randrange(1, MAX_POKEMON_NUMBER)
    game["score"] += 100 + game["streak"] * 10
    game["streak"] += 1
    return repository.save_game(game)


def get_round_outcome(game):
    """Pure decision, no side effects: what state is this round actually in?"""
    if not game["lives"]:
        return "game_over"
    if "_" in game["masked_name"]:
        return "guessing"
    return "won_round"


def get_game_state(game):
    """Orchestrates: checks the round outcome, applies the matching side effect
    (advance to next Pokemon / persist game-over), and returns what to display."""
    pokemon = pokemon_client.get_pokemon(game["pokedex_number"])
    outcome = get_round_outcome(game)
    current_app.logger.debug(
        f"get_game_state, name = {pokemon['name']}, outcome = {outcome}")

    if outcome == "guessing":
        return ("Who's That Pokémon?", repository.get_hi_score(), pokemon["silhouette"])

    if outcome == "won_round":
        load_next_pokemon(game)
    else:  # game_over
        repository.save_game(game)

    message = "It's {}!".format(pokemon["name"])
    return (message, repository.get_hi_score(), pokemon["original"])
