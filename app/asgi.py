import asyncio
from asyncio.proactor_events import _ProactorBasePipeTransport
from functools import wraps

from .config import config
from .app import create_app
from .models import parse_offers, SearchJSON, is_valid_payload

from fastapi import Request, Response
from starlette.responses import HTMLResponse


def silence_event_loop_closed(func):
    """Decorates pipe transport to silence messages about closed loop"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if str(e) != "Event loop is closed":
                raise

    return wrapper


_ProactorBasePipeTransport.__del__ = silence_event_loop_closed(
    _ProactorBasePipeTransport.__del__
)


app = create_app()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Handles homepage render"""
    return app.templates.TemplateResponse("base/index.html", {"request": request})


@app.post("/search", response_class=HTMLResponse)
async def search(request: Request, args: SearchJSON):
    """Handles search query"""
    args = args.dict()
    if not is_valid_payload(args):
        return Response(content="Invalid data", status_code=400)

    offers = await parse_offers(**args, parsers=config.PARSERS, semaphore=app.semaphore)
    return app.templates.TemplateResponse(
        "reports/search.html", {"request": request, "offers": offers}
    )
