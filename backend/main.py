from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import os

from database import init_db, create_document, get_documents

app = FastAPI(title="Portfolio API", version="1.0.0")

# CORS
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*" if FRONTEND_URL == "*" else FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models for contact form submissions
class ContactSubmission(BaseModel):
    name: str = Field(..., max_length=120)
    email: str = Field(..., max_length=160)
    message: str = Field(..., max_length=5000)
    company: Optional[str] = None
    topic: Optional[str] = None


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/")
async def root():
    return {"message": "Portfolio backend is live"}


@app.get("/test")
async def test():
    # Basic database diagnostics
    db = await init_db()
    try:
        names = await db.list_collection_names()
    except Exception as e:
        names = []
    return {
        "backend": "ok",
        "database": "connected",
        "database_url": os.getenv("DATABASE_URL", "mongodb://localhost:27017"),
        "database_name": os.getenv("DATABASE_NAME", "appdb"),
        "connection_status": "ok",
        "collections": names,
    }


@app.post("/contact")
async def submit_contact(payload: ContactSubmission):
    doc = await create_document("contact", payload.dict())
    if not doc:
        raise HTTPException(status_code=500, detail="Failed to store message")
    return {"status": "received", "id": doc.get("_id")}


# Simple projects listing for portfolio grid (optional demo data)
class Project(BaseModel):
    title: str
    subtitle: Optional[str] = None
    image: Optional[str] = None
    tags: List[str] = []
    url: Optional[str] = None


@app.get("/projects")
async def list_projects():
    # If collection empty, return a few curated demos for the UI
    docs = await get_documents("projects", {}, limit=32)
    if docs:
        return docs
    return [
        {
            "title": "MetaBloom",
            "subtitle": "Generative identity system",
            "image": "/covers/metabloom.jpg",
            "tags": ["gen-art", "branding", "webgl"],
            "url": "#"
        },
        {
            "title": "NEON/GRID",
            "subtitle": "Realtime shader microsite",
            "image": "/covers/neongrid.jpg",
            "tags": ["threejs", "shaders"],
            "url": "#"
        },
        {
            "title": "FOLD",
            "subtitle": "Experimental editorial",
            "image": "/covers/fold.jpg",
            "tags": ["typography", "motion"],
            "url": "#"
        }
    ]
