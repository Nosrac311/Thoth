from fastapi import APIRouter, Request

from fastapi.templating import Jinja2Templates

from database import get_restaurant_details


router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


@router.get("/restaurant")
def restaurant_page(
    request: Request,
    name: str
):

    history = get_restaurant_details(name)

    return templates.TemplateResponse(
        request=request,
        name="restaurant.html",
        context={
            "name": name,
            "history": history
        }
    )
