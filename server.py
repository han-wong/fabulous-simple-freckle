from werkzeug.exceptions import Forbidden
from flask import Flask
from flask import render_template
from flask import request

import os
import model

from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)


def verify_signature(payload_body, secret_token, signature_header):
    """Verify that the payload was sent from GitHub by validating SHA256.

    Raise and return 403 if not authorized.

    Args:
        (str) payload_body: original request body to verify (request.body())
        (bytes) secret_token: GitHub app webhook token (WEBHOOK_SECRET)
        (bytes) signature_header: header received from GitHub (x-hub-signature-256)
    """
    import hashlib
    import hmac

    if not signature_header:
        return Forbidden(description="x-hub-signature-256 header is missing!")

    hash_object = hmac.new(secret_token, msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = ("sha256=" + hash_object.hexdigest()).encode()
    if not hmac.compare_digest(expected_signature, signature_header):
        return Forbidden(description="Request signatures didn't match!")


app = Flask(__name__)
app.config.update(SECRET_KEY=os.environ.get("SECRET_KEY"))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/result", methods=["GET", "POST"])
def result():
    if request.method == "POST" and len(dict(request.form)) > 0:
        userdata = dict(request.form)
        book = userdata["book"]
        character = model.get_character(book)
        gif_url = model.get_gif(character)
        return render_template("result.html", character=character, gif_url=gif_url)
    else:
        return "Sorry, there was an error."


@app.route("/git", methods=["GET", "POST"])
def git():
    if request.method == "POST":
        PAYLOAD = request.get_data()
        TOKEN = os.environ.get("WEBHOOK").encode()
        HEADER = request.headers.get("X-Hub-Signature-256").encode()

        if len(PAYLOAD) > 1 * 1024 * 1024:
            return Forbidden(description="Payload bigger than 1 MB")

        verify_signature(PAYLOAD, TOKEN, HEADER)

        git_message = keep_up_to_date_with_main()
        os.system("refresh")
        return git_message

    return "<h1>Testing the Flask Application Factory Pattern</h1>"


def keep_up_to_date_with_main():
    import subprocess

    git_message = subprocess.check_output("git reset --hard HEAD", shell=True)
    git_message += subprocess.check_output("git pull", shell=True)
    return git_message


if __name__ == "__main__":
    app.run()
