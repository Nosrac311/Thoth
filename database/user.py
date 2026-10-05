from database.connection import get_connection


def init():

    db = get_connection()

    db.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            email TEXT NOT NULL UNIQUE,

            password_hash TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    db.commit()
    db.close()


# --------------------------------------------------
# USERS
# --------------------------------------------------


def create_user(email, password_hash):

    db = get_connection()

    cursor = db.cursor()

    try:

        cursor.execute("""
            INSERT INTO users (
                email,
                password_hash
            )
            VALUES (?, ?)
        """, (
            email.lower().strip(),
            password_hash,
        ))

        db.commit()

        user_id = cursor.lastrowid

        return user_id

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()

        print(
        "CREATED USER:",
            user_id,
            email
        )



def get_user_by_email(email):

    db = get_connection()

    cursor = db.cursor()

    cursor.execute("""
        SELECT
            id,
            email,
            password_hash
        FROM users
        WHERE email = ?
    """, (
        email.lower().strip(),
    ))

    row = cursor.fetchone()

    db.close()

    if row is None:
        return None

    return {
        "id": row[0],
        "email": row[1],
        "password_hash": row[2],
    }




def get_user_by_id(user_id):

    db = get_connection()

    cursor = db.cursor()

    cursor.execute("""
        SELECT
            id,
            email,
            password_hash
        FROM users
        WHERE id = ?
    """, (
        user_id,
    ))

    row = cursor.fetchone()

    db.close()

    if row is None:
        return None

    return {
        "id": row[0],
        "email": row[1],
        "password_hash": row[2],
    }
