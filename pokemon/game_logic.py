import re
import random
from flask import current_app
from pokemon import game_repository
from pokemon import pokemon_client
from pokemon import pokemon_repository

# Characters that map to a guessable A-Z equivalent
CHAR_MAP = {
    "É": "E",
    "♀": "F",
    "♂": "M",
    "2": "TWO",
}
MIN_POKEMON_NUMBER = 1
MAX_POKEMON_NUMBER = 899


def normalize_name(name):
    """Convert a raw Pokémon name to a guessable form using only A-Z and spaces.
    Non-letter characters are either transliterated via CHAR_MAP or dropped.
    Runs of spaces are collapsed to a single space and the result is stripped.
    Examples:
      "TYPE: NULL"  -> "TYPE NULL"
      "NIDORAN♀"   -> "NIDORAN F"
      "NIDORAN♂"   -> "NIDORAN M"
      "MR. MIME"    -> "MR MIME"
      "FLABÉBÉ"    -> "FLABEBE"
      "HO-OH"       -> "HO OH"
      "PORYGON2"    -> "PORYGON TWO"
    """
    result = []

    for ch in name:
        if ch in CHAR_MAP:
            result.append(CHAR_MAP[ch])

        elif ch.isalpha():
            result.append(ch)

        else:
            # Replace any non-letter (space, hyphen, colon, period, etc.) with a space
            result.append(" ")

    return re.sub(r" +", " ", "".join(result)).strip()


def start_new_game(user_id=None):
    """Pick a random starting Pokemon and create a fresh game. Returns the new game_id."""
    starting_pokemon = random.randrange(MIN_POKEMON_NUMBER, MAX_POKEMON_NUMBER)
    return game_repository.create_game(starting_pokemon, user_id=user_id)


def load_game(game_id):
    """Fetch a game row and enrich it with the current masked display word."""

    game = game_repository.get_game(game_id)
    if game:
        game = dict(game)
        game["masked_name"] = get_masked_name(game)
        return game


def get_masked_name(game):
    """Build the partially-revealed Pokemon name, e.g. 'P _ _ H A _ H U'.
    Operates on the normalized name so every character is either a space
    (always shown) or an A-Z letter the player can actually guess.
    """

    pokemon = pokemon_client.get_pokemon(game["pokedex_number"])
    name = normalize_name(pokemon["name"])
    current_app.logger.debug(f"get_masked_name, normalized name = {name}")

    return " ".join(
        [
            letter if letter == " " or letter in game["guessed_letters"] else "_"
            for letter in name
        ]
    )


def handle_guess(game, letters):
    """Apply one or more new guessed letters in order, updating lives/streak/guessed_letters.
    Stops early if lives run out mid-batch. Writes to the database once, after the whole batch.
    """

    pokemon = pokemon_client.get_pokemon(game["pokedex_number"])
    name = normalize_name(pokemon["name"])
    changed = False

    for letter in letters.upper():
        if game["lives"] <= 0 or "_" not in game["masked_name"]:
            break

        if letter in game["guessed_letters"]:
            continue

        if letter not in name:
            game["lives"] -= 1
            game["streak"] = 0

        game["guessed_letters"] += letter
        game["masked_name"] = get_masked_name(game)
        changed = True

    if changed:
        game_repository.save_game(game)

    return load_game(game["game_id"])


def load_next_pokemon(game):
    """Round was won: award points, bump the streak, and move to a new Pokemon.

    Points = 100 base
           + difficulty bonus (0-100, based on community fail rate)
           + streak bonus (10 per round on current streak)
           + accuracy bonus (10 per life remaining when the round was solved).
    Lives are reset after scoring so the accuracy bonus uses the actual
    lives remaining at the moment the round ended.
    """
    difficulty_bonus = pokemon_repository.get_difficulty_bonus(game["pokedex_number"])
    game["score"] += 100 + difficulty_bonus + game["streak"] * 10 + game["lives"] * 10
    pokemon_repository.record_solved(game["pokedex_number"])
    game["streak"] += 1
    game["guessed_letters"] = ""
    game["lives"] = 7
    game["pokedex_number"] = random.randrange(MIN_POKEMON_NUMBER, MAX_POKEMON_NUMBER)
    return game_repository.save_game(game)


def is_game_owner(game, user_id):
    """Return True if the request is allowed to act on this game.

    Rules:
    - Guest games (no user_id) are open to anyone.
    - User-owned games may only be acted on by that user.
    """
    return game.get("user_id") is None or game.get("user_id") == user_id


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
        f"get_game_state, name = {pokemon['name']}, outcome = {outcome}"
    )

    if outcome == "guessing":
        return (
            "Who's That Pokémon?",
            game_repository.get_hi_score(),
            pokemon["silhouette"],
        )

    if outcome == "won_round":
        load_next_pokemon(game)
    else:  # game_over
        pokemon_repository.record_failed(game["pokedex_number"])
        game_repository.save_game(game)

    message = "It's {}!".format(pokemon["name"])
    return (message, game_repository.get_hi_score(), pokemon["original"])
