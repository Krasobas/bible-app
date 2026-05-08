from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, RefPage
from app.schemas import RefPageCreate, RefPageUpdate, RefPageResponse, RefPageListItem
from app.deps import verify_api_key, get_course_or_404

router = APIRouter()


def _ref_or_404(course_id: int, slug: str, db: Session) -> RefPage:
    ref = db.query(RefPage).filter(RefPage.course_id == course_id, RefPage.slug == slug).first()
    if not ref:
        raise HTTPException(status_code=404, detail="Reference page not found")
    return ref


@router.get("/", response_model=list[RefPageListItem])
def list_ref_pages(course_slug: str, db: Session = Depends(get_db)):
    course = get_course_or_404(course_slug, db)
    return db.query(RefPage).filter(RefPage.course_id == course.id).order_by(RefPage.sort_order).all()


@router.get("/{ref_slug}", response_model=RefPageResponse)
def get_ref_page(course_slug: str, ref_slug: str, db: Session = Depends(get_db)):
    course = get_course_or_404(course_slug, db)
    return _ref_or_404(course.id, ref_slug, db)


@router.post("/", response_model=RefPageResponse, status_code=201, dependencies=[Depends(verify_api_key)])
def create_ref_page(course_slug: str, data: RefPageCreate, db: Session = Depends(get_db)):
    course = get_course_or_404(course_slug, db)
    if db.query(RefPage).filter(RefPage.course_id == course.id, RefPage.slug == data.slug).first():
        raise HTTPException(status_code=409, detail=f"Reference page '{data.slug}' already exists")
    ref = RefPage(course_id=course.id, **data.model_dump())
    db.add(ref)
    db.commit()
    db.refresh(ref)
    return ref


@router.put("/{ref_slug}", response_model=RefPageResponse, dependencies=[Depends(verify_api_key)])
def update_ref_page(course_slug: str, ref_slug: str, data: RefPageUpdate, db: Session = Depends(get_db)):
    course = get_course_or_404(course_slug, db)
    ref = _ref_or_404(course.id, ref_slug, db)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(ref, key, value)
    db.commit()
    db.refresh(ref)
    return ref


@router.delete("/{ref_slug}", status_code=204, dependencies=[Depends(verify_api_key)])
def delete_ref_page(course_slug: str, ref_slug: str, db: Session = Depends(get_db)):
    course = get_course_or_404(course_slug, db)
    ref = _ref_or_404(course.id, ref_slug, db)
    db.delete(ref)
    db.commit()
