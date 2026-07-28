from database.connection import get_connection


def init():

    db = get_connection()

    db.execute("""
    CREATE TABLE IF NOT EXISTS restaurant_stats (

        source TEXT,
        restaurant TEXT,
        mean_interval REAL,
        variance REAL,
        count INTEGER,

        PRIMARY KEY(
            source,
            restaurant
        )
    )
    """)


# ---------------- STATS ----------------


def update_stats(source, restaurant, new_interval):

    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
        SELECT
            mean_interval,
            variance,
            count

        FROM restaurant_stats

        WHERE restaurant = ?
        AND source = ?

    """,
                   (
                       restaurant,
                       source
                   ))

    row = cursor.fetchone()

    if row is None:

        mean = new_interval
        variance = 10.0
        count = 1

    else:

        mean, variance, count = row

        count += 1

        previous_mean = mean

        mean = (
            mean
            +
            (new_interval - mean) / count
        )

        variance = (
            variance
            +
            (
                (new_interval - previous_mean) ** 2
                -
                variance
            )
            /
            count
        )

    cursor.execute("""
        INSERT OR REPLACE INTO restaurant_stats
        (
            source,
            restaurant,
            mean_interval,
            variance,
            count
        )

        VALUES (?,?,?,?,?)

    """,
                   (
                       source,
                       restaurant,
                       mean,
                       variance,
                       count
                   ))

    db.commit()
    db.close()


def get_distribution_params(restaurant, source):

    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
        SELECT
            mean_interval,
            variance

        FROM restaurant_stats

        WHERE restaurant = ?
        AND source = ?

    """,
                   (
                       restaurant,
                       source
                   ))

    row = cursor.fetchone()

    db.close()

    if not row:

        # fallback if restaurant has no history
        return 120, 400

    return row


def inspection_dates(restaurant):

    db = get_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT inspection_date
        FROM inspections
        WHERE restaurant = ?
        ORDER BY inspection_date ASC
        """,
        (
            restaurant,
        )
    )

    dates = [
        row[0]
        for row in cursor.fetchall()
    ]

    db.close()

    return dates
