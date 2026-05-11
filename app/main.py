import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routers import api_courses, api_lectures, api_reference, api_images, web

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")

app = FastAPI(
    title="Библейский кружок",
    description="API для управления контентом библейского кружка: курсы, лекции, справочные страницы.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Static files (CSS, JS)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# API routes
app.include_router(api_courses.router, prefix="/api/courses", tags=["Курсы"])
app.include_router(api_lectures.router, prefix="/api/courses/{course_slug}/lectures", tags=["Лекции"])
app.include_router(api_reference.router, prefix="/api/courses/{course_slug}/reference", tags=["Справка"])
app.include_router(api_images.router, prefix="/api/images", tags=["Изображения"])

# Web pages (must be last — catch-all path patterns)
app.include_router(web.router)


@app.on_event("startup")
def startup():
    init_db()
    _migrate_add_category()


def _migrate_add_category():
    """Add 'category' column to courses table if it doesn't exist (one-time migration)."""
    from sqlalchemy import text, inspect
    from app.database import engine
    with engine.connect() as conn:
        insp = inspect(engine)
        columns = [c["name"] for c in insp.get_columns("courses")]
        if "category" not in columns:
            conn.execute(text("ALTER TABLE courses ADD COLUMN category VARCHAR DEFAULT ''"))
            conn.commit()
