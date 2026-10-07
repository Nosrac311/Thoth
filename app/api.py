from dotenv import load_dotenv

load_dotenv()


import logging
import os
import sys


from fastapi import (
    FastAPI,
    Query,
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
