from fastapi import APIRouter, Request

from fastapi.templating import Jinja2Templates

from database import get_inspector_details


router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


# Web dashboard route
@router.get("/inspector")
def inspector_page(
    request: Request,
    inspector_id: str
):

    stats, history = get_inspector_details(inspector_id)

    return templates.TemplateResponse(
        request=request,
        name="inspector.html",
        context={
            "inspector_id": inspector_id,
            "stats": stats,
            "history": history
        }
    )


# Mobile app API route
@router.get("/inspectors/{inspector_id}")
def inspector_api(inspector_id: str):

    stats, history = get_inspector_details(inspector_id)

    if not stats:
        return {
            "error": "Inspector not found"
        }

    return {
        "inspector_id": inspector_id,
        "statistics": {
            "total_inspections": stats[1],
            "average_score": stats[2]
        },
        "history": [
            {
                "restaurant": row[0],
                "date": row[1],
                "score": row[2],
                "grade": row[3]
            }
            for row in history
        ]
    }
