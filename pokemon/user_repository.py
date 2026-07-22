from pokemon.database import get_db


def get_user(user_id):
    """Fetch a user row by Supabase user_id, or None if not found."""
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM app_user WHERE user_id = %s", (user_id,))
    return cur.fetchone()


def is_display_name_taken(display_name, exclude_user_id=None):
    """Check whether a display_name is already in use by another user.

    Pass exclude_user_id to allow the current user to keep their existing name
    without triggering a collision (i.e. when updating, not creating).
    """
    db = get_db()
    cur = db.cursor()
    if exclude_user_id:
        cur.execute(
            "SELECT 1 FROM app_user WHERE display_name = %s AND user_id != %s",
            (display_name, exclude_user_id),
        )
    else:
        cur.execute(
            "SELECT 1 FROM app_user WHERE display_name = %s",
            (display_name,),
        )
    return cur.fetchone() is not None


def create_user(user_id, display_name):
    """Insert a new app_user row. Raises ValueError on name collision."""
    if is_display_name_taken(display_name):
        raise ValueError(f"Display name '{display_name}' is already taken.")
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "INSERT INTO app_user (user_id, display_name) VALUES (%s, %s)",
        (user_id, display_name),
    )
    db.commit()
    return get_user(user_id)


def update_display_name(user_id, display_name):
    """Update an existing user's display_name. Raises ValueError on name collision."""
    if is_display_name_taken(display_name, exclude_user_id=user_id):
        raise ValueError(f"Display name '{display_name}' is already taken.")
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "UPDATE app_user SET display_name = %s, updated = NOW() WHERE user_id = %s",
        (display_name, user_id),
    )
    db.commit()
    return get_user(user_id)


def get_or_create_user(user_id, fallback_display_name):
    """Return the existing user row, or create one with a unique fallback name.

    If fallback_display_name is taken, appends a numeric suffix until unique.
    """
    user = get_user(user_id)
    if user:
        return user

    candidate = fallback_display_name
    suffix = 1
    while is_display_name_taken(candidate):
        candidate = f"{fallback_display_name}{suffix}"
        suffix += 1

    return create_user(user_id, candidate)
