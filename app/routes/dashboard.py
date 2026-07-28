from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from database import (
    get_inspection_count,
    get_latest_inspections,
    get_sources,
    get_channels
)


router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


@router.get("/dashboard")
def dashboard(request: Request):

    inspections = get_latest_inspections(50)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "inspections": inspections,
            "total": get_inspection_count(),
            "sources": get_sources(),
            "channels": get_channels()
        }
    )
