from database.connection import get_connection


# ============================================================
# INITIALIZE / MIGRATE
# ============================================================

def init():

    db = get_connection()

    columns = db.execute("""
        PRAGMA table_info(watchlist)
    """).fetchall()

    column_names = [
        column[1]
        for column in columns
    ]

    # --------------------------------------------------------
    # Create table if it does not exist
    # --------------------------------------------------------

    if not columns:

        db.execute("""
            CREATE TABLE watchlist (

                user_id INTEGER NOT NULL,

                keyword TEXT NOT NULL,

                PRIMARY KEY (
                    user_id,
                    keyword
                ),

                FOREIGN KEY (
                    user_id
                )
                REFERENCES users(id)
                ON DELETE CASCADE

            )
        """)

        db.commit()
        db.close()

        return

    # --------------------------------------------------------
    # Migrate old global watchlist
    # --------------------------------------------------------

    if "user_id" not in column_names:

        print(
            "⚠️ Migrating old watchlist table..."
        )

        db.execute("""
            ALTER TABLE watchlist
            RENAME TO watchlist_old
        """)

        db.execute("""
            CREATE TABLE watchlist (

                user_id INTEGER NOT NULL,

                keyword TEXT NOT NULL,

                PRIMARY KEY (
                    user_id,
                    keyword
                ),

                FOREIGN KEY (
                    user_id
                )
                REFERENCES users(id)
                ON DELETE CASCADE

            )
        """)

        # Old entries did not have a user_id,
        # so they cannot safely be assigned to anyone.

        db.execute("""
            DROP TABLE watchlist_old
        """)

        db.commit()

        print(
            "✅ Watchlist migration complete."
        )

    db.close()


# ============================================================
# USER WATCHLIST
# ============================================================

def get_watchlist(user_id):

    db = get_connection()

    cursor = db.cursor()

    cursor.execute("""
        SELECT keyword
        FROM watchlist
        WHERE user_id = ?
        ORDER BY keyword
    """, (
        user_id,
    ))

    rows = [
        row[0]
        for row in cursor.fetchall()
    ]

    db.close()

    return rows


# ============================================================
# ALL WATCHLIST KEYWORDS
#
# Used by the desktop launcher.
# ============================================================

def get_all_watchlist_keywords():

    db = get_connection()

    cursor = db.cursor()

    cursor.execute("""
        SELECT DISTINCT keyword
        FROM watchlist
        ORDER BY keyword
    """)

    rows = [
        row[0]
        for row in cursor.fetchall()
    ]

    db.close()

    return rows


# ============================================================
# ADD
# ============================================================

def add_to_watchlist(
    user_id,
    keyword
):

    keyword = str(
        keyword
    ).strip().upper()

    if not keyword:
        return

    db = get_connection()

    db.execute("""
        INSERT OR IGNORE INTO watchlist (
            user_id,
            keyword
        )
        VALUES (?, ?)
    """, (
        user_id,
        keyword,
    ))

    db.commit()
    db.close()


# ============================================================
# REMOVE
# ============================================================

def remove_from_watchlist(
    user_id,
    keyword
):

    keyword = str(
        keyword
    ).strip().upper()

    db = get_connection()

    db.execute("""
        DELETE FROM watchlist
        WHERE user_id = ?
        AND keyword = ?
    """, (
        user_id,
        keyword,
    ))

    db.commit()
    db.close()


# ============================================================
# CHECK ONE USER
# ============================================================

def is_watched(
    user_id,
    restaurant
):

    restaurant = str(
        restaurant
    ).upper()

    db = get_connection()

    cursor = db.cursor()

    cursor.execute("""
        SELECT keyword
        FROM watchlist
        WHERE user_id = ?
    """, (
        user_id,
    ))

    rows = cursor.fetchall()

    db.close()

    for row in rows:

        keyword = row[0]

        if keyword in restaurant:

            return True

    return False


# ============================================================
# CHECK ANY USER
#
# Used by desktop launcher.
# ============================================================

def is_watched_by_any_user(
    restaurant
):

    restaurant = str(
        restaurant
    ).upper()

    db = get_connection()

    cursor = db.cursor()

    cursor.execute("""
        SELECT keyword
        FROM watchlist
    """)

    rows = cursor.fetchall()

    db.close()

    for row in rows:

        keyword = row[0]

        if keyword in restaurant:

            return True

    return False


# ============================================================
# GET USERS WATCHING RESTAURANT
#
# Used by Discord monitor.
# ============================================================

def get_watchers(
    restaurant
):

    restaurant = str(
        restaurant
    ).upper()

    db = get_connection()

    cursor = db.cursor()

    cursor.execute("""
        SELECT
            user_id,
            keyword
        FROM watchlist
    """)

    rows = cursor.fetchall()

    db.close()

    watchers = []

    for user_id, keyword in rows:

        if keyword in restaurant:

            if user_id not in watchers:

                watchers.append(
                    user_id
                )

    return watchers


# ============================================================
# GET MATCHING KEYWORDS FOR USER
# ============================================================

def get_matching_keywords(
    user_id,
    restaurant
):

    restaurant = str(
        restaurant
    ).upper()

    db = get_connection()

    cursor = db.cursor()

    cursor.execute("""
        SELECT keyword
        FROM watchlist
        WHERE user_id = ?
    """, (
        user_id,
    ))

    rows = cursor.fetchall()

    db.close()

    matches = []

    for row in rows:

        keyword = row[0]

        if keyword in restaurant:

            matches.append(
                keyword
            )

    return matches


# ============================================================
# GET ALL USERS WATCHING WITH THEIR KEYWORDS
#
# Useful if notifications need to know exactly which
# keyword caused the match.
# ============================================================

def get_watchers_with_keywords(
    restaurant
):

    restaurant = str(
        restaurant
    ).upper()

    db = get_connection()

    cursor = db.cursor()

    cursor.execute("""
        SELECT
            user_id,
            keyword
        FROM watchlist
        ORDER BY user_id
    """)

    rows = cursor.fetchall()

    db.close()

    watchers = []

    for user_id, keyword in rows:

        if keyword in restaurant:

            watchers.append({
                "user_id": user_id,
                "keyword": keyword,
            })

    return watchers


# ============================================================
# CLEAR ONE USER
# ============================================================

def clear_watchlist(
    user_id
):

    db = get_connection()

    db.execute("""
        DELETE FROM watchlist
        WHERE user_id = ?
    """, (
        user_id,
    ))

    db.commit()
    db.close()


# ============================================================
# COUNT ONE USER'S WATCHLIST
# ============================================================

def get_watchlist_count(
    user_id
):

    db = get_connection()

    cursor = db.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM watchlist
        WHERE user_id = ?
    """, (
        user_id,
    ))

    count = cursor.fetchone()[0]

    db.close()

    return count
