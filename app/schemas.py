from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# ── Courses ──

class CourseCreate(BaseModel):
    slug: str = Field(..., pattern=r"^[a-z0-9-]+$", examples=["luke"])
    title: str = Field(..., examples=["Евангелие от Луки"])
    subtitle: str = ""
    description: str = ""
    course_type: str = Field("book", pattern=r"^(book|special)$")
    category: str = ""
    sort_order: int = 0


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    course_type: Optional[str] = Field(None, pattern=r"^(book|special)$")
    category: Optional[str] = None
    sort_order: Optional[int] = None


class CourseResponse(BaseModel):
    id: int
    slug: str
    title: str
    subtitle: str
    description: str
    course_type: str
    category: str
    sort_order: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


class CourseListItem(BaseModel):
    id: int
    slug: str
    title: str
    subtitle: str
    course_type: str
    category: str
    sort_order: int
    updated_at: datetime
    class Config:
        from_attributes = True


# ── Lectures ──

class LectureCreate(BaseModel):
    slug: str = Field(..., pattern=r"^[a-z0-9-]+$", examples=["1-2"])
    title: str = Field(..., examples=["Лк 1–2"])
    subtitle: str = ""
    chapter_start: Optional[int] = Field(None, ge=1, le=150)
    chapter_end: Optional[int] = Field(None, ge=1, le=150)
    content: str = ""
    sort_order: int = 0


class LectureUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    chapter_start: Optional[int] = Field(None, ge=1, le=150)
    chapter_end: Optional[int] = Field(None, ge=1, le=150)
    content: Optional[str] = None
    sort_order: Optional[int] = None


class LectureResponse(BaseModel):
    id: int
    course_id: int
    slug: str
    title: str
    subtitle: str
    chapter_start: Optional[int]
    chapter_end: Optional[int]
    content: str
    sort_order: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


class LectureListItem(BaseModel):
    id: int
    slug: str
    title: str
    subtitle: str
    chapter_start: Optional[int]
    chapter_end: Optional[int]
    sort_order: int
    updated_at: datetime
    class Config:
        from_attributes = True


# ── Reference pages ──

class RefPageCreate(BaseModel):
    slug: str = Field(..., pattern=r"^[a-z0-9-]+$", examples=["chronology"])
    title: str = Field(..., examples=["Хронология"])
    content: str = ""
    sort_order: int = 0


class RefPageUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    sort_order: Optional[int] = None


class RefPageResponse(BaseModel):
    id: int
    course_id: int
    slug: str
    title: str
    content: str
    sort_order: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


class RefPageListItem(BaseModel):
    id: int
    slug: str
    title: str
    sort_order: int
    updated_at: datetime
    class Config:
        from_attributes = True


# ── Status ──

class StatusResponse(BaseModel):
    courses: list[CourseListItem]
    images: list[str]
