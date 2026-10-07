import sqlite3
import os
import sys


def database_directory():

    database_dir = os.getenv("DATABASE_DIR")

    if database_dir:

        os.makedirs(
            database_dir,
            exist_ok=True
        )

        return database_dir

    if getattr(sys, "frozen", False):

        base = os.path.dirname(
            sys.executable
        )

    else:

        base = os.path.dirname(
            os.path.abspath(__file__)
        )

    return base


def database_path():

    return os.path.join(
        database_directory(),
        "inspections.db"
    )


def users_database_path():

    return os.path.join(
        database_directory(),
        "users.db"
    )


def get_connection():

    path = database_path()

    db = sqlite3.connect(path)

    db.execute(
        "PRAGMA journal_mode=WAL;"
    )

    return db


def get_users_connection():

    path = users_database_path()

    db = sqlite3.connect(path)

    db.execute(
        "PRAGMA journal_mode=WAL;"
    )

    db.execute(
        "PRAGMA foreign_keys = ON;"
    )

    return db
