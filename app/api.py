from dotenv import load_dotenv

load_dotenv()


import logging
import os
import sys
import sqlite3
import tempfile
import shutil

from fastapi import (
    FastAPI,
    Query,
    UploadFile,
    File,
    Header,
    HTTPException,
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from fastapi.middleware.cors import CORSMiddleware

import uvicorn


from app.routes import (
    dashboard,
    restaurant,
    inspector,
    channels,
    auth,
    watchlist,
)


from database import (
    get_inspection_count,
    search_restaurant,
    get_latest_inspections,
)


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="Restaurant Inspection API",
    description="API for restaurant inspection data",
    version="1.0",
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(
    dashboard.router
)

app.include_router(
    restaurant.router
)

app.include_router(
    inspector.router
)

app.include_router(
    channels.router
)

app.include_router(
    auth.router
)

app.include_router(
    watchlist.router
)


# ============================================================
# DATABASE CONFIGURATION
#
# Render:
#
# DATABASE_DIR=/data
#
# Local development:
# falls back to the normal application directory.
# ============================================================

DATABASE_DIR = os.getenv(
    "DATABASE_DIR"
)

if DATABASE_DIR:

    os.makedirs(
        DATABASE_DIR,
        exist_ok=True
    )

else:

    DATABASE_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )


DATABASE_MIGRATION_TOKEN = os.getenv(
    "DATABASE_MIGRATION_TOKEN"
)


MIGRATION_DATABASE = os.path.join(
    DATABASE_DIR,
    "inspections.db"
)


# ============================================================
# STATIC FILES
# ============================================================

def resource_path(relative_path):

    if getattr(
        sys,
        "frozen",
        False
    ):

        base_path = sys._MEIPASS

    else:

        base_path = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

    return os.path.join(
        base_path,
        relative_path
    )


app.mount(
    "/static",
    StaticFiles(
        directory=resource_path(
            "app/static"
        )
    ),
    name="static",
)


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "online"
    }


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return RedirectResponse(
        "/dashboard"
    )


# ============================================================
# STATS
# ============================================================

@app.get("/stats")
def stats():

    return {
        "total_inspections":
            get_inspection_count()
    }


# ============================================================
# RESTAURANT SEARCH
# ============================================================

@app.get("/restaurants/search")
def restaurant_search(
    name: str = Query(
        ...,
        description="Restaurant name to search",
    )
):

    results = search_restaurant(
        name
    )

    return {
        "query": name,

        "results": [

            {
                "restaurant": row[0],
                "date": row[1],
                "score": row[2],
                "grade": row[3],
            }

            for row in results
        ],
    }


# ============================================================
# LATEST INSPECTIONS
# ============================================================

@app.get("/inspections/latest")
def latest_inspections(
    limit: int = 50
):

    results = get_latest_inspections(
        limit
    )

    return {
        "count": len(results),

        "inspections": [

            {
                "restaurant": row[0],
                "date": row[1],
                "score": row[2],
                "grade": row[3],
                "county": row[4],
                "inspector_id": row[5],
            }

            for row in results
        ],
    }


# ============================================================
# TEMPORARY DATABASE MIGRATION
#
# THIS ENDPOINT IS ONLY FOR THE ONE-TIME MIGRATION OF:
#
#     local database/inspections.db
#
# TO:
#
#     /data/inspections.db
#
# Once the migration has been verified, DELETE THIS ENTIRE
# ENDPOINT AND REMOVE DATABASE_MIGRATION_TOKEN FROM RENDER.
# ============================================================

@app.post(
    "/admin/migrate-database"
)
async def migrate_database(
    database: UploadFile = File(...),

    x_migration_token: str | None = Header(
        default=None
    ),
):

    # --------------------------------------------------------
    # Verify migration token
    # --------------------------------------------------------

    if not DATABASE_MIGRATION_TOKEN:

        raise HTTPException(
            status_code=500,
            detail=(
                "DATABASE_MIGRATION_TOKEN "
                "is not configured."
            ),
        )


    if (
        x_migration_token
        != DATABASE_MIGRATION_TOKEN
    ):

        raise HTTPException(
            status_code=401,
            detail="Unauthorized.",
        )


    # --------------------------------------------------------
    # NEVER overwrite an existing database
    # --------------------------------------------------------

    if os.path.exists(
        MIGRATION_DATABASE
    ):

        raise HTTPException(
            status_code=409,
            detail=(
                "Database already exists at "
                f"{MIGRATION_DATABASE}. "
                "Migration refused."
            ),
        )


    # --------------------------------------------------------
    # Make sure the persistent directory exists
    # --------------------------------------------------------

    os.makedirs(
        DATABASE_DIR,
        exist_ok=True
    )


    temp_path = None


    try:

        # ----------------------------------------------------
        # Create temporary database file
        # ----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".db",
            dir=DATABASE_DIR,
        ) as temp_file:

            temp_path = (
                temp_file.name
            )


            # ------------------------------------------------
            # Copy upload to temporary file
            # ------------------------------------------------

            while True:

                chunk = await database.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                temp_file.write(
                    chunk
                )


        # ----------------------------------------------------
        # Verify SQLite database
        # ----------------------------------------------------

        db = sqlite3.connect(
            temp_path
        )


        try:

            # ------------------------------------------------
            # SQLite integrity check
            # ------------------------------------------------

            integrity = db.execute(
                "PRAGMA integrity_check;"
            ).fetchone()[0]


            if integrity != "ok":

                raise RuntimeError(
                    "SQLite integrity check failed: "
                    + str(integrity)
                )


            # ------------------------------------------------
            # Find tables
            # ------------------------------------------------

            tables = db.execute("""
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """).fetchall()


            table_info = {}


            # ------------------------------------------------
            # Count rows in every table
            # ------------------------------------------------

            for row in tables:

                table_name = row[0]


                quoted_name = (
                    '"'
                    + table_name.replace(
                        '"',
                        '""'
                    )
                    + '"'
                )


                count = db.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM {quoted_name}
                    """
                ).fetchone()[0]


                table_info[
                    table_name
                ] = count


        finally:

            db.close()


        # ----------------------------------------------------
        # Move verified database into final location
        # ----------------------------------------------------

        shutil.move(
            temp_path,
            MIGRATION_DATABASE
        )


        temp_path = None


        # ----------------------------------------------------
        # Success
        # ----------------------------------------------------

        logging.info(
            "Database migration completed."
        )


        return {

            "success": True,

            "database":
                MIGRATION_DATABASE,

            "integrity":
                integrity,

            "tables":
                table_info,

        }


    except Exception as error:

        # ----------------------------------------------------
        # Remove failed temporary upload
        # ----------------------------------------------------

        if (
            temp_path
            and os.path.exists(
                temp_path
            )
        ):

            os.remove(
                temp_path
            )


        logging.exception(
            "Database migration failed"
        )


        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

@app.get("/admin/inspect-database")
def inspect_database(
    x_migration_token: str | None = Header(
        default=None
    )
):

    # --------------------------------------------------------
    # Verify migration token
    # --------------------------------------------------------

    if not DATABASE_MIGRATION_TOKEN:

        raise HTTPException(
            status_code=500,
            detail=(
                "DATABASE_MIGRATION_TOKEN "
                "is not configured."
            )
        )

    if (
        x_migration_token
        != DATABASE_MIGRATION_TOKEN
    ):

        raise HTTPException(
            status_code=401,
            detail="Unauthorized."
        )

    # --------------------------------------------------------
    # Check whether database exists
    # --------------------------------------------------------

    if not os.path.exists(
        MIGRATION_DATABASE
    ):

        raise HTTPException(
            status_code=404,
            detail=(
                "Database does not exist at "
                f"{MIGRATION_DATABASE}"
            )
        )

    db = None

    try:

        db = sqlite3.connect(
            MIGRATION_DATABASE
        )

        # ----------------------------------------------------
        # Integrity check
        # ----------------------------------------------------

        integrity = db.execute(
            "PRAGMA integrity_check;"
        ).fetchone()[0]

        # ----------------------------------------------------
        # Get tables
        # ----------------------------------------------------

        tables = db.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """).fetchall()

        table_info = {}

        for row in tables:

            table_name = row[0]

            quoted_name = (
                '"'
                + table_name.replace(
                    '"',
                    '""'
                )
                + '"'
            )

            count = db.execute(
                f"""
                SELECT COUNT(*)
                FROM {quoted_name}
                """
            ).fetchone()[0]

            table_info[
                table_name
            ] = count

        # ----------------------------------------------------
        # File information
        # ----------------------------------------------------

        file_size = os.path.getsize(
            MIGRATION_DATABASE
        )

        return {
            "database": MIGRATION_DATABASE,
            "exists": True,
            "size_bytes": file_size,
            "integrity": integrity,
            "tables": table_info
        }

    finally:

        if db is not None:
            db.close()



# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,

    format=(
        "%(asctime)s | %(message)s"
    ),
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "*"
    ],

    allow_credentials=False,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
)


# ============================================================
# RUN SERVER
# ============================================================

def run_dashboard():

    uvicorn.run(
        "app.api:app",

        host="0.0.0.0",

        port=int(
            os.getenv(
                "PORT",
                "8000"
            )
        ),

        log_config=None,

        access_log=True,
    )


# ============================================================
# LOCAL ENTRY POINT
# ============================================================

if __name__ == "__main__":

    run_dashboard()
