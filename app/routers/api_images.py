import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db, ImageRecord, Course
from app.deps import verify_api_key

router = APIRouter()

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "images")
os.makedirs(IMAGE_DIR, exist_ok=True)


@router.post("/", status_code=201, dependencies=[Depends(verify_api_key)])
async def upload_image(
    file: UploadFile = File(...),
    course_slug: str | None = None,
    db: Session = Depends(get_db),
):
    """Upload an image. Optionally associate with a course via query param ?course_slug=luke."""
    # Determine filename
    original = file.filename or "image.png"
    name, ext = os.path.splitext(original)
    # Ensure unique filename
    filename = original
    dest = os.path.join(IMAGE_DIR, filename)
    if os.path.exists(dest):
        filename = f"{name}-{uuid.uuid4().hex[:8]}{ext}"
        dest = os.path.join(IMAGE_DIR, filename)

    # Write file
    content = await file.read()
    with open(dest, "wb") as f:
        f.write(content)

    # Record in DB
    course_id = None
    if course_slug:
        course = db.query(Course).filter(Course.slug == course_slug).first()
        if course:
            course_id = course.id

    record = ImageRecord(filename=filename, mime_type=file.content_type or "image/png", course_id=course_id)
    db.add(record)
    db.commit()
    db.refresh(record)

    return {"filename": filename, "url": f"/img/{filename}"}


@router.get("/")
def list_images(db: Session = Depends(get_db)):
    records = db.query(ImageRecord).all()
    return [{"filename": r.filename, "url": f"/img/{r.filename}"} for r in records]


@router.delete("/{filename}", status_code=204, dependencies=[Depends(verify_api_key)])
def delete_image(filename: str, db: Session = Depends(get_db)):
    record = db.query(ImageRecord).filter(ImageRecord.filename == filename).first()
    if not record:
        raise HTTPException(status_code=404, detail="Image not found")
    # Remove file
    path = os.path.join(IMAGE_DIR, filename)
    if os.path.exists(path):
        os.remove(path)
    db.delete(record)
    db.commit()
