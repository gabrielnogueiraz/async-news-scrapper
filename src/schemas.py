from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class NewsBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    url: HttpUrl


class NewsCreate(NewsBase):
    pass


class NewsResponse(NewsBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime


class ScrapeResponse(BaseModel):
    success: bool
    news_added: int
    message: str


class ErrorResponse(BaseModel):
    detail: str
