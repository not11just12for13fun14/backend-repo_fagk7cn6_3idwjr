import os
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents

app = FastAPI(title="Vienna Theatre API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Pydantic response models (lightweight for responses) ----------
class InfoOut(BaseModel):
    name: str
    address: str
    city: str
    country: str
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    description_de: Optional[str] = None
    description_en: Optional[str] = None
    how_to_get_de: Optional[str] = None
    how_to_get_en: Optional[str] = None
    video_reel_url: Optional[str] = None


class OwnerOut(BaseModel):
    name: str
    role: str
    bio_de: str
    bio_en: str
    avatar: Optional[str] = None


class EventOut(BaseModel):
    title: str
    description: Optional[str] = None
    date: datetime
    language: str
    category: str
    duration_min: Optional[int] = None
    ticket_url: Optional[str] = None
    cover_image: Optional[str] = None


# ---------- Helpers ----------

def ensure_seed_data():
    """Seed minimal content if collections are empty."""
    if db is None:
        return

    # Info
    if db["info"].count_documents({}) == 0:
        create_document(
            "info",
            {
                "name": "Kabarett & Impro Wien",
                "address": "Kreativgasse 12",
                "city": "Wien",
                "country": "Österreich",
                "phone": "+43 1 234 5678",
                "email": "hello@kabarett-impro.wien",
                "website": "https://kabarett-impro.wien",
                "description_de": "Ein quirliges Zuhause für Kabarett, Stand-up und Impro in Wien.",
                "description_en": "A quirky home for cabaret, stand-up, and improv in Vienna.",
                "how_to_get_de": "U3 bis Volkstheater, dann 5 Minuten zu Fuß. Straßenbahn 49 bis Siebensternplatz.",
                "how_to_get_en": "U3 to Volkstheater, then a 5-minute walk. Tram 49 to Siebensternplatz.",
                "video_reel_url": "https://player.vimeo.com/video/76979871?h=8272103f6e",
            },
        )

    # Owners
    if db["owner"].count_documents({}) == 0:
        owners = [
            {
                "name": "Lena Leitner",
                "role": "Künstlerische Leitung",
                "bio_de": "Improverin, Kabarettistin und professionelle Quatschmacherin.",
                "bio_en": "Improviser, cabaret artist and professional mischief maker.",
                "avatar": "https://i.pravatar.cc/200?img=5",
            },
            {
                "name": "Max Maurer",
                "role": "Geschäftsführung",
                "bio_de": "Organisationswitz mit Herz für Pointen und Publikum.",
                "bio_en": "Organizational wizard with a heart for punchlines and people.",
                "avatar": "https://i.pravatar.cc/200?img=12",
            },
        ]
        for o in owners:
            create_document("owner", o)

    # Events (next months)
    if db["event"].count_documents({}) == 0:
        base_date = datetime.utcnow().replace(hour=19, minute=30, second=0, microsecond=0)
        events = [
            {
                "title": "Kabarett: Wiener Schmäh",
                "description": "Pointenreicher Abend mit lokalen Talenten.",
                "date": base_date + timedelta(days=7),
                "language": "de",
                "category": "Kabarett",
                "duration_min": 90,
                "ticket_url": "https://tickets.example.com/kabarett-wiener-schmaeh",
                "cover_image": "https://images.unsplash.com/photo-1515165562835-c3b8c935f746?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "title": "Improv: Alles kann, nix muss",
                "description": "Publikumsvorschläge führen zu wilden Szenen.",
                "date": base_date + timedelta(days=18),
                "language": "de",
                "category": "Impro",
                "duration_min": 80,
                "ticket_url": "https://tickets.example.com/improv-alles-kann",
                "cover_image": "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "title": "Stand-up: Late Night Laughs",
                "description": "Englischsprachige Comedians aus ganz Europa.",
                "date": base_date + timedelta(days=32),
                "language": "en",
                "category": "Stand-up",
                "duration_min": 100,
                "ticket_url": "https://tickets.example.com/late-night-laughs",
                "cover_image": "https://images.unsplash.com/photo-1487537023671-8dce1a785863?q=80&w=1200&auto=format&fit=crop",
            },
        ]
        for e in events:
            # pymongo can't store naive datetime without tz info set consistently; accepted in this env
            create_document("event", e)


@app.on_event("startup")
async def startup_event():
    try:
        ensure_seed_data()
    except Exception:
        # Seeding is best-effort; avoid crashing on startup
        pass


@app.get("/")
def read_root():
    return {"message": "Vienna Theatre API running"}


@app.get("/api/info", response_model=InfoOut)
def get_info():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    doc = db["info"].find_one({}, sort=[("created_at", -1)])
    if not doc:
        raise HTTPException(status_code=404, detail="Info not found")
    doc.pop("_id", None)
    return doc


@app.get("/api/owners", response_model=List[OwnerOut])
def get_owners():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    owners = get_documents("owner")
    for o in owners:
        o.pop("_id", None)
    return owners


@app.get("/api/events", response_model=List[EventOut])
def get_events():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    events = list(db["event"].find({}).sort("date", 1))
    for e in events:
        e.pop("_id", None)
    return events


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
