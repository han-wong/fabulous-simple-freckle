import json

from flask import (
    Blueprint,
    session,
    request,flash,
    redirect,
    url_for,
    render_template,
)

from pokemon.database import get_db
from pokemon import game

bp = Blueprint("play", __name__)


@bp.route("/new")
def new_game():
    game_id = game.create(10)

    return redirect(url_for("play.play", game_id=game_id))


@bp.route("/play", methods=["GET", "POST"])
def play():
    if game_id := request.args.get("game_id"):
        game.load_game(game_id)
    else:
        return new_game()

    pokemon = game.load_pokemon()
    name = pokemon["name"].upper()
    print(f"{name = }")

    if request.method == "POST":
        value = request.json.get("value")
        if not value in name:
            session["life"] -= 1
            session["streak"] = 0
            flash(f"You lost a life!", category="error")

        session["guess_player"] += value
        game.save_game(game_id)
        return (
            json.dumps(
                {
                    "guess": game.get_guess(name),
                    "life": session.get("life"),
                    "streak": session.get("streak"),
                }
            ),
            200,
            {"ContentType": "application/json"},
        )

    else:
        print("pass")
        print(session["pokemon"])

    guess = game.get_guess(name)
    print(f"{guess = }")

    image = pokemon["original"]
    name = "It's {}!".format(pokemon["name"])
    if "_" in guess:
        image = pokemon["silhouette"]
        name = "Who's That Pokémon?"
    else:
        game.load_next_pokemon()
        game.save_game(game_id)

    return render_template(
        "pages/play.html",
        guess=guess,
        life=session.get("life"),
        name=name,
        pokemon=image,
        hi_score=session.get("hi-score"),
        score=session.get("score"),
        streak=session.get("streak"),
    )


@bp.route("/game_over")
def game_over():
    print("game_over")
    print(f'{session.get("life") = }')
    print(f'{session.get("score") = }')

    return (
        json.dumps(
            {
                "score": session.get("score"),
            }
        ),
        200,
        {"ContentType": "application/json"},
    )


@bp.route("/guess", methods=["GET"])
def guess():
    return (
        json.dumps(
            {
                "guess_exclude": session.get("guess_exclude"),
                "guess_player": session.get("guess_player"),
            }
        ),
        200,
        {"ContentType": "application/json"},
    )
