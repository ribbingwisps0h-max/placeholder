"""
Placeholder Image Service — FastAPI application entry-point.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import router

BASE_DIR = Path(__file__).parent

app = FastAPI(
    title="Placeholder Image Service",
    description="Generate custom placeholder images on the fly.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Static files
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Templates
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Register API router
app.include_router(router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    # `name` parameter is now second; first argument should be the request
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
async def health():
    return {"status": "ok"}
