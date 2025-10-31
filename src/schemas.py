from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class NewsBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    url: HttpUrl


class NewsCreate(NewsBase):
    pass


class NewsResponse(NewsBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ScrapeResponse(BaseModel):
    success: bool
    news_added: int
    message: str


class ErrorResponse(BaseModel):
    detail: str
