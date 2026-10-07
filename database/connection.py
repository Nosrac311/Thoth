import sqlite3
import os
import sys


# ============================================================
# APPLICATION DATABASE DIRECTORY
#
# inspections.db lives here.
#
# github_sync.py updates this database and pushes the updated
# database to GitHub.
# ============================================================

def database_directory():

    if getattr(
        sys,
        "frozen",
        False
    ):

        base = os.path.dirname(
            sys.executable
        )

    else:

        base = os.path.dirname(
            os.path.abspath(__file__)
        )

    return base


# ============================================================
# INSPECTIONS DATABASE
#
# NOT persistent.
#
# This database is updated through github_sync.py.
# ============================================================

def database_path():

    return os.path.join(
        database_directory(),
        "inspections.db"
    )


# ============================================================
# USERS DATABASE DIRECTORY
#
# ONLY users.db uses the Render Persistent Disk.
# ============================================================

def users_database_directory():

    persistent_directory = os.getenv(
        "DATABASE_DIR"
    )

    if persistent_directory:

        os.makedirs(
            persistent_directory,
            exist_ok=True
        )

        return persistent_directory

    # Local development fallback.
    #
    # This means users.db will be next to inspections.db
    # when running locally without DATABASE_DIR.

    return database_directory()


# ============================================================
# USERS DATABASE
# ============================================================

def users_database_path():

    return os.path.join(
        users_database_directory(),
        "users.db"
    )


# ============================================================
# INSPECTIONS CONNECTION
# ============================================================

def get_connection():

    path = database_path()

    db = sqlite3.connect(
        path
    )

    db.execute(
        "PRAGMA journal_mode=WAL;"
    )

    return db


# ============================================================
# USERS CONNECTION
# ============================================================

def get_users_connection():

    path = users_database_path()

    db = sqlite3.connect(
        path
    )

    db.execute(
        "PRAGMA journal_mode=WAL;"
    )

    db.execute(
        "PRAGMA foreign_keys = ON;"
    )

    return db
