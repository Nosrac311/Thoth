import uuid

from database.connection import get_connection


def init():

    db = get_connection()

    db.execute("""
    CREATE TABLE IF NOT EXISTS channels (

        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS messages (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel_id TEXT NOT NULL,
        author TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(channel_id)
        REFERENCES channels(id)
        ON DELETE CASCADE

    )
    """)

    db.execute("""
    CREATE INDEX IF NOT EXISTS idx_messages_channel
    ON messages(channel_id)
    """)

    db.commit()
    db.close()


def create_channel(name, description=""):

    channel_id = str(uuid.uuid4())

    db = get_connection()

    db.execute("""
        INSERT INTO channels
        (
            id,
            name,
            description
        )
        VALUES (?, ?, ?)
    """,
               (
                   channel_id,
                   name,
                   description
               ))

    db.commit()
    db.close()

    return channel_id


def get_channels():

    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
    SELECT id,name,description
    FROM channels
    ORDER BY name
    """)

    rows = cursor.fetchall()

    db.close()

    return rows


def get_messages(channel_id):

    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
    SELECT
        author,
        content,
        created_at

    FROM messages

    WHERE channel_id=?

    ORDER BY created_at
    """,
                   (channel_id,))

    rows = cursor.fetchall()

    db.close()

    return rows


def create_message(channel_id, author, content):

    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
    INSERT INTO messages
    (
        channel_id,
        author,
        content
    )
    VALUES (?,?,?)
    """,
                   (
                       channel_id,
                       author,
                       content
                   ))

    db.commit()
    db.close()


def delete_channel(channel_id):

    db = get_connection()
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM messages WHERE channel_id=?",
        (channel_id,)
    )

    cursor.execute(
        "DELETE FROM channels WHERE id=?",
        (channel_id,)
    )

    db.commit()
    db.close()


def rename_channel(channel_id, new_name):

    db = get_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        UPDATE channels
        SET name = ?
        WHERE id = ?
        """,
        (
            new_name,
            channel_id
        )
    )

    db.commit()
    db.close()


def get_inspector_channel(inspector_id):

    db = get_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT channel_id
        FROM inspector_channels
        WHERE inspector_id = ?
        """,
        (str(inspector_id),)
    )

    row = cursor.fetchone()

    db.close()

    return row[0] if row else None


def save_inspector_channel(inspector_id, channel_id):

    db = get_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO inspector_channels
        (
            inspector_id,
            channel_id
        )
        VALUES (?,?)
        """,
        (
            str(inspector_id),
            channel_id
        )
    )

    db.commit()
    db.close()
