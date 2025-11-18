import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, LookbookEntry, LoyaltyUser, JournalPost

app = FastAPI(title="Éclat de Lune API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"brand": "Éclat de Lune", "tagline": "Wear the sky."}


@app.get("/test")
def test_database():
    """Quick connectivity check"""
    resp = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "collections": [],
    }
    try:
        if db is not None:
            resp["database"] = "✅ Connected"
            resp["collections"] = db.list_collection_names()
        return resp
    except Exception as e:
        resp["database"] = f"❌ {str(e)[:120]}"
        return resp


# ---------- Product Endpoints ----------

@app.get("/api/products", response_model=List[Product])
def list_products(category: Optional[str] = None):
    filt = {"category": category} if category else {}
    docs = get_documents("product", filt)
    # Convert Mongo _id to string-less dict for pydantic
    for d in docs:
        d.pop("_id", None)
    return docs


@app.get("/api/products/{slug}", response_model=Product)
def get_product(slug: str):
    docs = get_documents("product", {"slug": slug}, limit=1)
    if not docs:
        raise HTTPException(status_code=404, detail="Product not found")
    doc = docs[0]
    doc.pop("_id", None)
    return doc


class CreateProductRequest(Product):
    pass


@app.post("/api/products")
def create_product(payload: CreateProductRequest):
    new_id = create_document("product", payload)
    return {"id": new_id}


# ---------- Lookbook Endpoints ----------

@app.get("/api/lookbook/{season}", response_model=List[LookbookEntry])
def get_lookbook(season: str):
    docs = get_documents("lookbookentry", {"season": season})
    docs.sort(key=lambda d: d.get("order", 0))
    for d in docs:
        d.pop("_id", None)
    return docs


# ---------- Loyalty Endpoints ----------

@app.get("/api/universe/profile", response_model=LoyaltyUser)
def get_profile(email: str):
    docs = get_documents("loyaltyuser", {"email": email}, limit=1)
    if not docs:
        # Auto-provision a new profile
        profile = LoyaltyUser(email=email)
        create_document("loyaltyuser", profile)
        return profile
    doc = docs[0]
    doc.pop("_id", None)
    return doc


class PhotonEvent(BaseModel):
    email: str
    kind: str  # view_3d, share_ar, recycle
    amount: int = 5


@app.post("/api/universe/earn")
def earn_photons(event: PhotonEvent):
    docs = get_documents("loyaltyuser", {"email": event.email}, limit=1)
    if not docs:
        profile = LoyaltyUser(email=event.email, photons=event.amount)
        create_document("loyaltyuser", profile)
        return {"ok": True}
    doc = docs[0]
    photons = int(doc.get("photons", 0)) + int(event.amount)
    db["loyaltyuser"].update_one({"_id": doc["_id"]}, {"$set": {"photons": photons}})
    return {"ok": True, "photons": photons}


# ---------- Journal Endpoints (minimal) ----------

@app.get("/api/journal", response_model=List[JournalPost])
def list_journal():
    docs = get_documents("journalpost")
    for d in docs:
        d.pop("_id", None)
    return docs


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
