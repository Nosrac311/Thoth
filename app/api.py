import logging
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
import sys
from app.routes import (
    dashboard,
    restaurant,
    inspector,
    channels
)

from database import (
    get_inspection_count,
    search_restaurant,
    get_latest_inspections
)
import uvicorn

from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Restaurant Inspection API",
    description="API for restaurant inspection data",
    version="1.0"
)


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


def resource_path(relative_path):

    if getattr(sys, "frozen", False):

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
        directory=resource_path("app/static")
    ),
    name="static"
)


@app.get("/health")
def health():

    return {
        "status": "online"
    }


@app.get("/")
def home():

    return RedirectResponse("/dashboard")


@app.get("/stats")
def stats():

    return {
        "total_inspections": get_inspection_count()
    }


@app.get("/restaurants/search")
def restaurant_search(
    name: str = Query(
        ...,
        description="Restaurant name to search"
    )
):

    results = search_restaurant(name)

    return {
        "query": name,
        "results": [
            {
                "restaurant": row[0],
                "date": row[1],
                "score": row[2],
                "grade": row[3]
            }
            for row in results
        ]
    }


@app.get("/inspections/latest")
def latest_inspections(
    limit: int = 50
):

    results = get_latest_inspections(limit)

    return {
        "count": len(results),

        "inspections": [
            {
                "restaurant": row[0],
                "date": row[1],
                "score": row[2],
                "grade": row[3],
                "county": row[4],
                "inspector_id": row[5]
            }

            for row in results
        ]
    }


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def run_dashboard():

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=None,
        access_log=True
    )


if __name__ == "__main__":

    run_dashboard()
