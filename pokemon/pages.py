from flask import Blueprint, make_response, redirect, render_template, request, session, url_for, flash

from pokemon import game_logic
from pokemon import user_repository
from pokemon.auth import get_current_user

bp = Blueprint("pages", __name__)



@bp.route("/")

def home():

    active_game_id = session.get("game_id")

    active_game = None

    if active_game_id:

        game = game_logic.load_game(active_game_id)

        if game and game["lives"] > 0:

            active_game = game

    return render_template("pages/home.html", active_game=active_game)



@bp.route("/about")

def about():

    return render_template("pages/about.html")



@bp.route("/auth")

def auth():

    return render_template("pages/auth.html")



@bp.route("/logout")

def logout():

    response = make_response(redirect(url_for("pages.home")))

    response.delete_cookie("sb_access_token")
    return response


@bp.route("/profile", methods=["GET", "POST"])
def profile():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("pages.auth"))

    user = user_repository.get_user(current_user["id"])
    error = None

    if request.method == "POST":
        display_name = request.form.get("display_name", "").strip()
        if len(display_name) < 3 or len(display_name) > 20:
            error = "Name must be between 3 and 20 characters."
        else:
            try:
                if user:
                    user = user_repository.update_display_name(current_user["id"], display_name)
                else:
                    user = user_repository.create_user(current_user["id"], display_name)
                return redirect(url_for("pages.profile"))
            except ValueError as e:
                error = str(e)

    return render_template("pages/profile.html", user=user, error=error)