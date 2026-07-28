

from database.connection import get_connection


def init():

    db = get_connection()

    db.execute("""
    CREATE TABLE IF NOT EXISTS watchlist (

        keyword TEXT PRIMARY KEY

    )
    """)

    db.commit()
    db.close()


# ---------------- WATCHLIST ----------------


def get_watchlist():

    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
        SELECT keyword
        FROM watchlist
        ORDER BY keyword
    """)

    rows = [
        row[0]
        for row in cursor.fetchall()
    ]

    db.close()

    return rows


def add_to_watchlist(keyword):

    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO watchlist
        (
            keyword
        )
        VALUES (?)
    """,
                   (
                       keyword.upper(),
                   ))

    db.commit()
    db.close()


def remove_from_watchlist(keyword):

    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
        DELETE FROM watchlist
        WHERE keyword = ?
    """,
                   (
                       keyword.upper(),
                   ))

    db.commit()
    db.close()


def is_watched(restaurant):

    restaurant = restaurant.upper()

    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
        SELECT keyword
        FROM watchlist
    """)

    keywords = cursor.fetchall()

    db.close()

    for row in keywords:

        if row[0] in restaurant:

            return True

    return False


def clear_watchlist():

    db = get_connection()

    db.execute("""
        DELETE FROM watchlist
    """)

    db.commit()
    db.close()
