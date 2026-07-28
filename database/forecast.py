

from database.connection import get_connection


def init():

    db = get_connection()

    db.execute("""
    CREATE TABLE IF NOT EXISTS forecast_messages (

        county TEXT PRIMARY KEY,
        message_id INTEGER NOT NULL

    )
    """)

    db.commit()
    db.close()


def get_forecast_message(county):

    db = get_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT message_id
        FROM forecast_messages
        WHERE county=?
        """,
        (county,)
    )

    row = cursor.fetchone()

    db.close()

    return row[0] if row else None


def save_forecast_message(county, message_id):

    db = get_connection()

    db.execute(
        """
        INSERT INTO forecast_messages
        (
            county,
            message_id
        )
        VALUES (?, ?)

        ON CONFLICT(county)
        DO UPDATE SET
            message_id = excluded.message_id
        """,
        (
            county,
            message_id
        )
    )

    db.commit()
    db.close()
