from database.connection import get_connection


def init():

    db = get_connection()

    db.execute("""
        CREATE TABLE IF NOT EXISTS inspections (

            state_id TEXT,
            inspection_date TEXT,
            restaurant TEXT,
            inspector_id TEXT,
            score TEXT,
            grade TEXT,
            source TEXT,
            location TEXT,

            PRIMARY KEY(
                source,
                state_id,
                inspection_date
            )
        )
    """)

    columns = db.execute("""
        PRAGMA table_info(inspections)
    """).fetchall()

    column_names = [
        column[1]
        for column in columns
    ]

    if "location" not in column_names:

        db.execute("""
            ALTER TABLE inspections
            ADD COLUMN location TEXT
        """)

    db.commit()

    db.close()


# --------------------------------------------------
# INSPECTION COUNT
# --------------------------------------------------

def get_inspection_count():

    db = get_connection()

    cursor = db.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM inspections
    """)

    count = cursor.fetchone()[0]

    db.close()

    return count


# --------------------------------------------------
# CHECK IF INSPECTION EXISTS
# --------------------------------------------------

def inspection_exists(
    source,
    state_id,
    inspection_date,
):

    db = get_connection()

    cursor = db.cursor()

    cursor.execute("""
        SELECT 1
        FROM inspections
        WHERE source = ?
        AND state_id = ?
        AND inspection_date = ?
    """, (
        source,
        state_id,
        inspection_date,
    ))

    result = cursor.fetchone()

    db.close()

    return result is not None


# --------------------------------------------------
# SAVE INSPECTION
# --------------------------------------------------

def save_inspection(
    source,
    data,
):

    db = get_connection()

    db.execute("""
        INSERT INTO inspections
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["id"],
        data["date"],
        data["name"],
        data["inspector_id"],
        data["score"],
        data["grade"],
        data["source"],
        data["location"],
    ))

    db.commit()

    db.close()


# --------------------------------------------------
# GET SOURCES
# --------------------------------------------------

def get_sources():

    db = get_connection()

    cursor = db.cursor()

    cursor.execute("""
        SELECT DISTINCT source
        FROM inspections
    """)

    rows = [
        row[0]
        for row in cursor.fetchall()
    ]

    db.close()

    return rows


# --------------------------------------------------
# LATEST INSPECTIONS
# --------------------------------------------------

def get_latest_inspections(
    limit=100000,
):

    db = get_connection()

    cursor = db.cursor()

    cursor.execute("""
        SELECT
            restaurant,
            inspection_date,
            score,
            grade,
            source,
            inspector_id,
            location

        FROM inspections

        ORDER BY inspection_date DESC

        LIMIT ?
    """, (
        limit,
    ))

    rows = cursor.fetchall()

    db.close()

    return rows


# --------------------------------------------------
# RESTAURANT DETAILS
# --------------------------------------------------

def get_restaurant_details(
    name,
):

    db = get_connection()

    cursor = db.cursor()

    cursor.execute("""
        SELECT
            restaurant,
            inspection_date,
            score,
            grade,
            source,
            inspector_id,
            location

        FROM inspections

        WHERE restaurant LIKE ?

        ORDER BY inspection_date ASC
    """, (
        f"%{name}%",
    ))

    rows = cursor.fetchall()

    db.close()

    return rows


# --------------------------------------------------
# RESTAURANT HISTORY
# --------------------------------------------------

def get_restaurant_history(
    name: str,
    source: str,
):

    db = get_connection()

    cursor = db.cursor()

    cursor.execute("""
        SELECT inspection_date

        FROM inspections

        WHERE restaurant LIKE ?

        AND source = ?

        ORDER BY inspection_date ASC
    """, (
        f"%{name}%",
        source,
    ))

    rows = [
        row[0]
        for row in cursor.fetchall()
    ]

    db.close()

    return rows


# --------------------------------------------------
# INSPECTOR DETAILS
# --------------------------------------------------

def get_inspector_details(
    inspector_id,
):

    db = get_connection()

    cursor = db.cursor()

    cursor.execute("""
        SELECT
            inspector_id,
            COUNT(*),
            AVG(CAST(score AS INTEGER))

        FROM inspections

        WHERE inspector_id = ?

        GROUP BY inspector_id
    """, (
        str(inspector_id),
    ))

    stats = cursor.fetchone()


    cursor.execute("""
        SELECT
            restaurant,
            inspection_date,
            score,
            grade,
            source,
            inspector_id,
            location

        FROM inspections

        WHERE inspector_id = ?

        ORDER BY inspection_date DESC
    """, (
        str(inspector_id),
    ))

    history = cursor.fetchall()

    db.close()

    return stats, history


# --------------------------------------------------
# SEARCH RESTAURANT
# --------------------------------------------------

def search_restaurant(
    name,
    limit=10,
):

    db = get_connection()

    cursor = db.cursor()

    cursor.execute("""
        SELECT
            restaurant,
            inspection_date,
            score,
            grade

        FROM inspections

        WHERE restaurant LIKE ?

        ORDER BY inspection_date DESC

        LIMIT ?
    """, (
        f"%{name}%",
        limit,
    ))

    rows = cursor.fetchall()

    db.close()

    return rows


# --------------------------------------------------
# WATCHLIST MATCHES
#
# Used by the desktop launcher.
#
# The launcher does not have a logged-in user, so
# this checks keywords belonging to ANY user.
#
# It does not expose which user owns a keyword.
# --------------------------------------------------

def get_watchlist_matches():

    from database.watchlist import (
        get_all_watchlist_keywords,
    )

    keywords = get_all_watchlist_keywords()


    if not keywords:

        return []


    db = get_connection()

    cursor = db.cursor()


    conditions = []

    params = []


    for keyword in keywords:

        keyword = keyword.strip()

        if not keyword:
            continue


        conditions.append(
            "UPPER(restaurant) LIKE ?"
        )

        params.append(
            f"%{keyword.upper()}%"
        )


    if not conditions:

        db.close()

        return []


    query = """
        SELECT
            restaurant,
            inspection_date,
            score,
            grade,
            inspector_id,
            state_id,
            source,
            location

        FROM inspections

        WHERE
    """


    query += " OR ".join(
        conditions
    )


    query += """
        ORDER BY inspection_date DESC
    """


    cursor.execute(
        query,
        params,
    )


    rows = cursor.fetchall()

    db.close()

    return rows
