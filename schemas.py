"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime

# Theatre-specific schemas

class Event(BaseModel):
    """
    Events collection schema
    Collection name: "event"
    """
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field(None, description="Short description")
    date: datetime = Field(..., description="Event date and time")
    language: str = Field("de", description="Language of performance: de/en")
    category: str = Field("Kabarett", description="Category like Kabarett, Impro, Stand-up")
    duration_min: Optional[int] = Field(None, description="Duration in minutes")
    ticket_url: Optional[HttpUrl] = Field(None, description="External ticket URL")
    cover_image: Optional[HttpUrl] = Field(None, description="Image for the event")

class Owner(BaseModel):
    """
    Owners collection schema
    Collection name: "owner"
    """
    name: str
    role: str
    bio_de: str
    bio_en: str
    avatar: Optional[HttpUrl] = None

class Info(BaseModel):
    """
    General theatre info
    Collection name: "info"
    """
    name: str
    address: str
    city: str
    country: str
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[HttpUrl] = None
    description_de: Optional[str] = None
    description_en: Optional[str] = None
    how_to_get_de: Optional[str] = None
    how_to_get_en: Optional[str] = None
    video_reel_url: Optional[HttpUrl] = None

# Keep example schemas for reference
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
