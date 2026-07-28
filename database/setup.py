from database.connection import get_connection


def initialize_database():

    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inspections (
        state_id TEXT,
        inspection_date TEXT,
        restaurant TEXT,
        inspector_id TEXT,
        score TEXT,
        grade TEXT,
        source TEXT,
        PRIMARY KEY(source,state_id,inspection_date)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS channels (

        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    cursor.execute("""
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

    db.commit()
    db.close()
