from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def _now():
    return datetime.now(timezone.utc)


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    subtitle = Column(String, default="")
    description = Column(Text, default="")
    course_type = Column(String, default="book")  # "book" | "special"
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    lectures = relationship("Lecture", back_populates="course", order_by="Lecture.sort_order")
    ref_pages = relationship("RefPage", back_populates="course", order_by="RefPage.sort_order")


class Lecture(Base):
    __tablename__ = "lectures"
    __table_args__ = (UniqueConstraint("course_id", "slug", name="uq_lecture_course_slug"),)

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    slug = Column(String, nullable=False)
    title = Column(String, nullable=False)
    subtitle = Column(String, default="")
    chapter_start = Column(Integer, nullable=True)
    chapter_end = Column(Integer, nullable=True)
    content = Column(Text, default="")
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    course = relationship("Course", back_populates="lectures")


class RefPage(Base):
    __tablename__ = "ref_pages"
    __table_args__ = (UniqueConstraint("course_id", "slug", name="uq_ref_course_slug"),)

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    slug = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, default="")
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    course = relationship("Course", back_populates="ref_pages")


class ImageRecord(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    filename = Column(String, unique=True, index=True, nullable=False)
    mime_type = Column(String, default="image/png")
    created_at = Column(DateTime, default=_now)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
