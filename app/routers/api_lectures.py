from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, Course, Lecture
from app.schemas import LectureCreate, LectureUpdate, LectureResponse, LectureListItem
from app.deps import verify_api_key, get_course_or_404

router = APIRouter()


def _lecture_or_404(course_id: int, slug: str, db: Session) -> Lecture:
    lec = db.query(Lecture).filter(Lecture.course_id == course_id, Lecture.slug == slug).first()
    if not lec:
        raise HTTPException(status_code=404, detail="Lecture not found")
    return lec


@router.get("/", response_model=list[LectureListItem])
def list_lectures(course_slug: str, db: Session = Depends(get_db)):
    course = get_course_or_404(course_slug, db)
    return db.query(Lecture).filter(Lecture.course_id == course.id).order_by(Lecture.sort_order).all()


@router.get("/{lecture_slug}", response_model=LectureResponse)
def get_lecture(course_slug: str, lecture_slug: str, db: Session = Depends(get_db)):
    course = get_course_or_404(course_slug, db)
    return _lecture_or_404(course.id, lecture_slug, db)


@router.post("/", response_model=LectureResponse, status_code=201, dependencies=[Depends(verify_api_key)])
def create_lecture(course_slug: str, data: LectureCreate, db: Session = Depends(get_db)):
    course = get_course_or_404(course_slug, db)
    if db.query(Lecture).filter(Lecture.course_id == course.id, Lecture.slug == data.slug).first():
        raise HTTPException(status_code=409, detail=f"Lecture '{data.slug}' already exists in this course")
    lecture = Lecture(course_id=course.id, **data.model_dump())
    db.add(lecture)
    db.commit()
    db.refresh(lecture)
    return lecture


@router.put("/{lecture_slug}", response_model=LectureResponse, dependencies=[Depends(verify_api_key)])
def update_lecture(course_slug: str, lecture_slug: str, data: LectureUpdate, db: Session = Depends(get_db)):
    course = get_course_or_404(course_slug, db)
    lecture = _lecture_or_404(course.id, lecture_slug, db)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(lecture, key, value)
    db.commit()
    db.refresh(lecture)
    return lecture


@router.delete("/{lecture_slug}", status_code=204, dependencies=[Depends(verify_api_key)])
def delete_lecture(course_slug: str, lecture_slug: str, db: Session = Depends(get_db)):
    course = get_course_or_404(course_slug, db)
    lecture = _lecture_or_404(course.id, lecture_slug, db)
    db.delete(lecture)
    db.commit()
