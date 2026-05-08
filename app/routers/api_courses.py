from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, Course
from app.schemas import CourseCreate, CourseUpdate, CourseResponse, CourseListItem
from app.deps import verify_api_key

router = APIRouter()


@router.get("/", response_model=list[CourseListItem])
def list_courses(db: Session = Depends(get_db)):
    return db.query(Course).order_by(Course.sort_order).all()


@router.get("/_status/overview")
def status_overview(db: Session = Depends(get_db)):
    """Overview of all content in the system."""
    from app.database import Lecture, RefPage, ImageRecord
    courses = db.query(Course).order_by(Course.sort_order).all()
    result = []
    for c in courses:
        lectures = db.query(Lecture).filter(Lecture.course_id == c.id).order_by(Lecture.sort_order).all()
        refs = db.query(RefPage).filter(RefPage.course_id == c.id).order_by(RefPage.sort_order).all()
        result.append({
            "slug": c.slug,
            "title": c.title,
            "course_type": c.course_type,
            "lectures": [{"slug": l.slug, "title": l.title} for l in lectures],
            "ref_pages": [{"slug": r.slug, "title": r.title} for r in refs],
        })
    images = db.query(ImageRecord).all()
    return {
        "courses": result,
        "images": [i.filename for i in images],
    }


@router.get("/{course_slug}", response_model=CourseResponse)
def get_course(course_slug: str, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.slug == course_slug).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/", response_model=CourseResponse, status_code=201, dependencies=[Depends(verify_api_key)])
def create_course(data: CourseCreate, db: Session = Depends(get_db)):
    if db.query(Course).filter(Course.slug == data.slug).first():
        raise HTTPException(status_code=409, detail=f"Course '{data.slug}' already exists")
    course = Course(**data.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.put("/{course_slug}", response_model=CourseResponse, dependencies=[Depends(verify_api_key)])
def update_course(course_slug: str, data: CourseUpdate, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.slug == course_slug).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(course, key, value)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_slug}", status_code=204, dependencies=[Depends(verify_api_key)])
def delete_course(course_slug: str, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.slug == course_slug).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()
