"""
Database Schemas for Éclat de Lune

Each Pydantic model represents a collection in MongoDB.
Collection name is the lowercase of the class name.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class Product(BaseModel):
    """
    Products available in the store
    Collection: "product"
    """
    title: str = Field(..., description="Display name")
    slug: str = Field(..., description="URL slug, unique")
    description: Optional[str] = Field(None, description="Long description")
    price: float = Field(..., ge=0, description="Price in USD")
    category: Literal["New", "Ready-to-Wear", "Occasion", "Atelier"]
    images: List[str] = Field(default_factory=list, description="Image URLs (Cloudinary)")
    glb_url: Optional[str] = Field(None, description="GLB asset URL (Draco)")
    colorways: List[str] = Field(default_factory=list, description="Available colorway keys")
    sizes: List[str] = Field(default_factory=lambda: ["XS", "S", "M", "L", "XL"]) 
    co2_saved_kg: Optional[float] = Field(None, ge=0, description="CO2 saved vs. industry avg")
    in_stock: bool = Field(True)


class LookbookEntry(BaseModel):
    """
    Seasonal lookbook frames
    Collection: "lookbookentry"
    """
    season: str = Field(..., description="e.g., 'fall-24'")
    title: str
    slug: str
    image: str = Field(..., description="Hero image URL")
    product_slugs: List[str] = Field(default_factory=list)
    order: int = Field(0, description="Sort order")


class LoyaltyUser(BaseModel):
    """
    Loyalty / Universe program profile
    Collection: "loyaltyuser"
    """
    email: str
    photons: int = Field(0, ge=0)
    tier: Literal["Nova", "Lunar", "Eclipse"] = "Nova"


# Minimal Journal schema if needed later
class JournalPost(BaseModel):
    title: str
    slug: str
    cover: str
    content: Optional[str] = None
