import pytest
from pokemon import game_logic, pokemon_client, game_repository, pokemon_repository


def make_game(guessed_letters="", lives=7, score=0, streak=0, player=None,
              pokedex_number="25", game_id="test-game-id"):
    """Build a plain game dict matching the shape game_logic expects.
    Does NOT compute masked_name here — tests set it explicitly or via get_masked_name."""
    return {
        "game_id": game_id,
        "guessed_letters": guessed_letters,
        "lives": lives,
        "player": player,
        "pokedex_number": pokedex_number,
        "score": score,
        "streak": streak,
    }


def mock_pokemon(monkeypatch, name="PIKACHU"):
    """Replace pokemon_client.get_pokemon so no real HTTP call happens."""
    fake_pokemon = {"name": name, "original": "fake_original_b64", "silhouette": "fake_silhouette_b64"}
    monkeypatch.setattr(pokemon_client, "get_pokemon", lambda pokedex_number: fake_pokemon)
    return fake_pokemon


def mock_repository(monkeypatch, game):
    """Stub both save_game and get_game against the same in-memory game dict,
    simulating a read-after-write without touching a real database."""
    saved_calls = []

    def fake_save_game(g):
        saved_calls.append(dict(g))
        return g

    def fake_get_game(game_id):
        return game

    monkeypatch.setattr(game_repository, "save_game", fake_save_game)
    monkeypatch.setattr(game_repository, "get_game", fake_get_game)
    return saved_calls


# --- get_round_outcome: pure function, no mocking needed at all ---

def test_round_outcome_is_game_over_when_no_lives_left():
    game = make_game(lives=0, guessed_letters="XYZ")
    game["masked_name"] = "_ _ _ _ _ _ _"
    assert game_logic.get_round_outcome(game) == "game_over"


def test_round_outcome_is_guessing_when_letters_remain_hidden():
    game = make_game(lives=5)
    game["masked_name"] = "P _ _ A"
    assert game_logic.get_round_outcome(game) == "guessing"


def test_round_outcome_is_won_round_when_fully_revealed():
    game = make_game(lives=5)
    game["masked_name"] = "P I K A"
    assert game_logic.get_round_outcome(game) == "won_round"


def test_round_outcome_prioritizes_game_over_even_if_name_would_be_hidden():
    # If lives hit 0, it's game over regardless of how much of the name is revealed
    game = make_game(lives=0)
    game["masked_name"] = "P _ _ A"
    assert game_logic.get_round_outcome(game) == "game_over"


# --- get_masked_name ---

def test_get_masked_name_reveals_only_guessed_letters(app_context, monkeypatch):
    mock_pokemon(monkeypatch, name="PIKACHU")
    game = make_game(guessed_letters="PIA")
    result = game_logic.get_masked_name(game)
    assert result == "P I _ A _ _ _"


def test_get_masked_name_all_hidden_when_nothing_guessed(app_context, monkeypatch):
    mock_pokemon(monkeypatch, name="EEVEE")
    game = make_game(guessed_letters="")
    result = game_logic.get_masked_name(game)
    assert result == "_ _ _ _ _"


def test_get_masked_name_fully_revealed_when_all_letters_guessed(app_context, monkeypatch):
    mock_pokemon(monkeypatch, name="MEW")
    game = make_game(guessed_letters="MEW")
    result = game_logic.get_masked_name(game)
    assert result == "M E W"


# --- handle_guess ---

def test_handle_guess_correct_letter_does_not_cost_a_life(app_context, monkeypatch):
    mock_pokemon(monkeypatch, name="MEW")
    game = make_game(guessed_letters="", lives=7)
    game["masked_name"] = game_logic.get_masked_name(game)
    mock_repository(monkeypatch, game)

    result = game_logic.handle_guess(game, "M")

    assert result["lives"] == 7
    assert "M" in result["guessed_letters"]


def test_handle_guess_wrong_letter_costs_a_life_and_resets_streak(app_context, monkeypatch):
    mock_pokemon(monkeypatch, name="MEW")
    game = make_game(guessed_letters="", lives=7, streak=3)
    game["masked_name"] = game_logic.get_masked_name(game)
    mock_repository(monkeypatch, game)

    result = game_logic.handle_guess(game, "Z")

    assert result["lives"] == 6
    assert result["streak"] == 0


def test_handle_guess_batch_processes_multiple_letters_in_one_call(app_context, monkeypatch):
    mock_pokemon(monkeypatch, name="MEW")
    game = make_game(guessed_letters="", lives=7)
    game["masked_name"] = game_logic.get_masked_name(game)
    saved_calls = mock_repository(monkeypatch, game)

    result = game_logic.handle_guess(game, "MEW")

    assert result["lives"] == 7  # all three letters are correct
    assert "M" in result["guessed_letters"]
    assert "E" in result["guessed_letters"]
    assert "W" in result["guessed_letters"]
    # exactly one DB write for the whole batch, not one per letter
    assert len(saved_calls) == 1


def test_handle_guess_stops_processing_once_lives_run_out(app_context, monkeypatch):
    mock_pokemon(monkeypatch, name="MEW")
    game = make_game(guessed_letters="", lives=1)
    game["masked_name"] = game_logic.get_masked_name(game)
    mock_repository(monkeypatch, game)

    # "Z" is wrong (costs the last life), "Q" comes after and should never be applied
    result = game_logic.handle_guess(game, "ZQ")

    assert result["lives"] == 0
    assert "Q" not in result["guessed_letters"]


def test_handle_guess_ignores_letters_already_correctly_guessed(app_context, monkeypatch):
    # api.py is responsible for filtering out already-guessed letters before calling
    # handle_guess, but handle_guess itself should still behave safely if a repeat
    # letter slips through, since re-checking a correct letter shouldn't cost a life.
    mock_pokemon(monkeypatch, name="MEW")
    game = make_game(guessed_letters="M", lives=7)
    game["masked_name"] = game_logic.get_masked_name(game)
    mock_repository(monkeypatch, game)

    result = game_logic.handle_guess(game, "M")

    assert result["lives"] == 7


# --- load_next_pokemon ---

def test_load_next_pokemon_resets_round_state_and_scores_points(monkeypatch):
    game = make_game(guessed_letters="MEW", lives=3, score=100, streak=2)
    mock_repository(monkeypatch, game)
    monkeypatch.setattr(pokemon_repository, "get_difficulty_bonus", lambda pokedex_number: 0)
    monkeypatch.setattr(pokemon_repository, "record_solved", lambda pokedex_number: None)

    result = game_logic.load_next_pokemon(game)

    assert result["guessed_letters"] == ""
    assert result["lives"] == 7
    assert result["streak"] == 3  # incremented from 2
    # score = previous 100 + 100 base + difficulty 0 + (streak=2)*10 + (lives=3)*10 = 250
    assert result["score"] == 250