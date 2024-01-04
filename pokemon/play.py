import json

from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from pokemon import game

bp = Blueprint("play", __name__)


@bp.route("/guess", methods=["GET"])
def guess():
    return (
        json.dumps(
            {
                "guess": session.get("guess"),
            }
        ),
        200,
        {"ContentType": "application/json"},
    )


@bp.route("/hi_scores", methods=["GET"])
def hi_scores():
    games = game.get_games_by_score()
    for x in games:
        current_app.logger.debug(f"games = {dict(x)}")
    return render_template("pages/hi-scores.html", games=games)


@bp.route("/new_game")
def new_game():
    game_id = game.create(10)
    return redirect(url_for("play.play", game_id=game_id))


@bp.route("/play", methods=["GET", "POST"])
def play():
    game_id = request.args.get("game_id")
    if game_id and not game.load_game(game_id):
        return new_game()

    pokemon = game.load_pokemon()
    name = pokemon["name"].upper()

    if request.method == "POST" and request.is_json:
        value = request.json.get("value")
        current_app.logger.debug(f"value = {value}")

        if not value in name:
            session["life"] -= 1
            session["streak"] = 0

        session["guess"] += value
        game.save_game(game_id)

        return (
            json.dumps(
                {
                    "current_word": game.get_current_word(name),
                    "life": session["life"],
                    "streak": session["streak"],
                }
            ),
            200,
            {"ContentType": "application/json"},
        )

    if request.method == "POST" and request.form:
        current_app.logger.debug(f"request.form = {request.form}")
        player = request.form.get("player-name")

        if not session["player"] and 3 <= len(player) <= 10:
            session["player"] = player
            game.save_game(game_id)
            return redirect(url_for("play.hi_scores"))

    image = pokemon["original"]
    header = "It's {}!".format(name)

    current_word = game.get_current_word(name)
    if "_" in current_word and session["life"]:
        image = pokemon["silhouette"]
        header = "Who's That Pokémon?"
    else:
        current_app.logger.debug(f"session['life'] = { session['life']}")
        if session["life"]:
            game.load_next_pokemon()
            # return redirect(url_for("play.play", game_id=game_id))
        game.save_game(game_id)

    return render_template(
        "pages/play.html",
        alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        current_word=current_word,
        life=session["life"],
        header=header,
        hi_score=session["hi_score"],
        pokemon=image,
        score=session["score"],
        streak=session["streak"],
    )
