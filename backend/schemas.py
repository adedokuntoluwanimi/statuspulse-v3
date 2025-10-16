from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class SiteCreate(BaseModel):
    url: HttpUrl

class SiteOut(BaseModel):
    id: int
    url: str
    created_at: datetime

    class Config:
        from_attributes = True

class CheckOut(BaseModel):
    id: int
    site_id: int
    ok: bool
    status_code: Optional[int]
    response_time_ms: Optional[float]
    checked_at: datetime

    class Config:
        from_attributes = True
