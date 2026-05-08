import os

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db, Course, Lecture, RefPage
from app.deps import template_context

router = APIRouter()

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "images")


@router.get("/img/{filename}")
def serve_image(filename: str):
    path = os.path.join(IMAGE_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path)


@router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    ctx = template_context(request, db)
    courses = db.query(Course).order_by(Course.sort_order).all()
    # Attach lecture/ref counts
    for c in courses:
        c._lecture_count = db.query(Lecture).filter(Lecture.course_id == c.id).count()
        c._ref_count = db.query(RefPage).filter(RefPage.course_id == c.id).count()
    ctx["courses_with_counts"] = courses
    return templates.TemplateResponse("index.html", ctx)


@router.get("/{course_slug}/", response_class=HTMLResponse)
def course_page(course_slug: str, request: Request, db: Session = Depends(get_db)):
    ctx = template_context(request, db)
    course = db.query(Course).filter(Course.slug == course_slug).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    lectures = db.query(Lecture).filter(Lecture.course_id == course.id).order_by(Lecture.sort_order).all()
    ref_pages = db.query(RefPage).filter(RefPage.course_id == course.id).order_by(RefPage.sort_order).all()
    ctx.update(course=course, lectures=lectures, ref_pages=ref_pages)
    return templates.TemplateResponse("course.html", ctx)


@router.get("/{course_slug}/{lecture_slug}", response_class=HTMLResponse)
def lecture_page(course_slug: str, lecture_slug: str, request: Request, db: Session = Depends(get_db)):
    ctx = template_context(request, db)
    course = db.query(Course).filter(Course.slug == course_slug).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    lecture = db.query(Lecture).filter(Lecture.course_id == course.id, Lecture.slug == lecture_slug).first()
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")

    # Previous / next
    prev_lec = db.query(Lecture).filter(
        Lecture.course_id == course.id, Lecture.sort_order < lecture.sort_order
    ).order_by(Lecture.sort_order.desc()).first()
    next_lec = db.query(Lecture).filter(
        Lecture.course_id == course.id, Lecture.sort_order > lecture.sort_order
    ).order_by(Lecture.sort_order.asc()).first()
    ref_pages = db.query(RefPage).filter(RefPage.course_id == course.id).order_by(RefPage.sort_order).all()

    ctx.update(
        course=course, lecture=lecture,
        prev_lecture=prev_lec, next_lecture=next_lec,
        ref_pages=ref_pages,
    )
    return templates.TemplateResponse("lecture.html", ctx)


@router.get("/{course_slug}/ref/{ref_slug}", response_class=HTMLResponse)
def ref_page(course_slug: str, ref_slug: str, request: Request, db: Session = Depends(get_db)):
    ctx = template_context(request, db)
    course = db.query(Course).filter(Course.slug == course_slug).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    ref = db.query(RefPage).filter(RefPage.course_id == course.id, RefPage.slug == ref_slug).first()
    if not ref:
        raise HTTPException(status_code=404, detail="Reference page not found")
    lectures = db.query(Lecture).filter(Lecture.course_id == course.id).order_by(Lecture.sort_order).all()
    ref_pages = db.query(RefPage).filter(RefPage.course_id == course.id).order_by(RefPage.sort_order).all()
    ctx.update(course=course, ref_page=ref, lectures=lectures, ref_pages=ref_pages)
    return templates.TemplateResponse("reference.html", ctx)
