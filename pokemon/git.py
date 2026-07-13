import hashlib
import hmac
import os
import subprocess

from flask import Blueprint, abort, request
from werkzeug.exceptions import Forbidden

bp = Blueprint("git", __name__)


@bp.route("/git", methods=("GET", "POST"))
def git():
    if request.method == "POST":
        PAYLOAD = request.get_data()
        TOKEN = os.getenv("WEBHOOK").encode()
        HEADER = request.headers.get("X-Hub-Signature-256", "").encode()

        if len(PAYLOAD) > 1 * 1024 * 1024:
            abort(403, description="Payload bigger than 1 MB")

        verify_signature(PAYLOAD, TOKEN, HEADER)

        git_message = keep_up_to_date_with_main()
        return git_message

    return "<h1>Testing the Flask Application Factory Pattern</h1>"


def verify_signature(payload_body, secret_token, signature_header):
    """Verify that the payload was sent from GitHub by validating SHA256.

    Raises a 403 Forbidden if the signature is missing or does not match.

    Args:
        payload_body (bytes): original request body to verify
        secret_token (bytes): GitHub app webhook token (WEBHOOK env var)
        signature_header (bytes): header received from GitHub (x-hub-signature-256)
    """
    if not signature_header:
        abort(403, description="x-hub-signature-256 header is missing!")

    hash_object = hmac.new(secret_token, msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = ("sha256=" + hash_object.hexdigest()).encode()
    if not hmac.compare_digest(expected_signature, signature_header):
        abort(403, description="Request signatures didn't match!")


def keep_up_to_date_with_main():
    git_message = subprocess.check_output(["git", "fetch"])
    git_message += subprocess.check_output(["git", "reset", "--hard", "origin/main"])
    return git_message
