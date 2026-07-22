import jwt
from flask import current_app, g, request

_jwks_clients = {}


def _get_jwks_client():
    """One PyJWKClient per Supabase project, reused across requests so its
    internal key cache actually persists (rather than re-fetching every request)."""
    jwks_uri = f"{current_app.config['SUPABASE_URL']}/auth/v1/.well-known/jwks.json"
    if jwks_uri not in _jwks_clients:
        _jwks_clients[jwks_uri] = jwt.PyJWKClient(jwks_uri, cache_keys=True)
    return _jwks_clients[jwks_uri]


def get_current_user():
    """Read and verify the Supabase auth token from a cookie, if present.
    Returns a dict with 'id' and 'email', or None if not logged in / invalid token."""
    if "user" not in g:
        g.user = _load_user_from_cookie()
    return g.user


def _load_user_from_cookie():
    token = request.cookies.get("sb_access_token")
    if not token:
        return None

    try:
        jwks_client = _get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256"],
            audience="authenticated",
        )
    except jwt.PyJWTError as e:
        current_app.logger.debug(f"auth: invalid/expired token: {e}")
        return None

    return {
        "id": payload.get("sub"),
        "email": payload.get("email"),
    }


def inject_current_user():
    """Context processor: makes `current_user` available in every template."""
    return {"current_user": get_current_user()}
