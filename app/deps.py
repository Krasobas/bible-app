from fastapi import Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session

from app.config import API_KEY, SITE_TITLE, SITE_SUBTITLE
from app.database import get_db, SessionLocal, Course


def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """Dependency: require valid API key for write operations."""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


def template_context(request: Request, db: Session = Depends(get_db)) -> dict:
    """Common context for all Jinja2 templates."""
    courses = db.query(Course).order_by(Course.sort_order).all()
    return {
        "request": request,
        "site_title": SITE_TITLE,
        "site_subtitle": SITE_SUBTITLE,
        "courses": courses,
    }


def get_course_or_404(slug: str, db: Session = Depends(get_db)) -> Course:
    course = db.query(Course).filter(Course.slug == slug).first()
    if not course:
        raise HTTPException(status_code=404, detail=f"Course '{slug}' not found")
    return course
