import sqlite3
import os
import sys


def database_path():

    if getattr(sys, "frozen", False):

        base = os.path.dirname(
            sys.executable
        )

    else:

        base = os.path.dirname(
            os.path.abspath(__file__)
        )

    return os.path.join(
        base,
        "inspections.db"
    )


def get_connection():

    db = sqlite3.connect(
        database_path()
    )

    db.execute(
        "PRAGMA journal_mode=WAL;"
    )

    return db
