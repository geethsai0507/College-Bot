from pydantic import BaseModel, HttpUrl, EmailStr
from typing import Optional

class Faculty(BaseModel):
    name: str
    photo_url: Optional[HttpUrl] = None
    email: Optional[EmailStr] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    qualification: Optional[str] = None
    experience: Optional[str] = None
    
    class Config:
        extra = 'allow'
