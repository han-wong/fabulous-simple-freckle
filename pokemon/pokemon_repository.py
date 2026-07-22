from pokemon.database import get_db

MIN_SAMPLES = 10  # ignore fail rate until we have enough data


def record_solved(pokedex_number):
    """Increment the solved counter for a Pokémon."""
    db = get_db()
    cur = db.cursor()
    cur.execute(
        """INSERT INTO pokemon_stats (pokedex_number, solved, failed)
           VALUES (%s, 1, 0)
           ON CONFLICT (pokedex_number)
           DO UPDATE SET solved = pokemon_stats.solved + 1""",
        (str(pokedex_number),),
    )
    db.commit()


def record_failed(pokedex_number):
    """Increment the failed counter for a Pokémon."""
    db = get_db()
    cur = db.cursor()
    cur.execute(
        """INSERT INTO pokemon_stats (pokedex_number, solved, failed)
           VALUES (%s, 0, 1)
           ON CONFLICT (pokedex_number)
           DO UPDATE SET failed = pokemon_stats.failed + 1""",
        (str(pokedex_number),),
    )
    db.commit()


def get_difficulty_bonus(pokedex_number):
    """Return a bonus score (0–100) based on community fail rate.

    Returns 0 if fewer than MIN_SAMPLES attempts have been recorded,
    so a brand-new Pokémon doesn't get an artificially high or low bonus.
    """
    db = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT solved, failed FROM pokemon_stats WHERE pokedex_number = %s",
        (str(pokedex_number),),
    )
    row = cur.fetchone()
    if not row:
        return 0

    total = row["solved"] + row["failed"]
    if total < MIN_SAMPLES:
        return 0

    fail_rate = row["failed"] / total
    return round(fail_rate * 100)
