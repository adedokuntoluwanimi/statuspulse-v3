import asyncio
import aiohttp
import time
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import crud
from database import Base, engine, get_db
from schemas import SiteCreate, SiteOut, CheckOut
from models import Site

app = FastAPI(title="StatusPulse API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
scheduler = AsyncIOScheduler()

@app.post("/sites", response_model=SiteOut)
def add_site(payload: SiteCreate, db: Session = Depends(get_db)):
    return crud.create_site(db, payload.url)

@app.get("/sites", response_model=list[SiteOut])
def get_sites(db: Session = Depends(get_db)):
    return crud.list_sites(db)

async def check_site(site: Site, db: Session):
    start = time.perf_counter()
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(site.url, timeout=10) as resp:
                duration = (time.perf_counter() - start) * 1000.0
                ok = 200 <= resp.status < 400
                crud.record_check(db, site.id, ok, resp.status, duration)
        except Exception:
            duration = (time.perf_counter() - start) * 1000.0
            crud.record_check(db, site.id, False, None, duration)

async def check_all_sites():
    from database import SessionLocal
    db = SessionLocal()
    sites = crud.list_sites(db)
    for s in sites:
        await check_site(s, db)
    db.close()

@scheduler.scheduled_job("interval", minutes=5)
async def scheduled_check():
    await check_all_sites()

@app.on_event("startup")
async def start_scheduler():
    scheduler.start()

@app.get("/status/{site_id}")
async def check_status(site_id: int, db: Session = Depends(get_db)):
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    start = time.perf_counter()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(site.url, timeout=10) as resp:
                duration = (time.perf_counter() - start) * 1000.0
                ok = 200 <= resp.status < 400
                crud.record_check(db, site.id, ok, resp.status, duration)
                return {
                    "url": site.url,
                    "online": ok,
                    "status_code": resp.status,
                    "response_time_ms": round(duration, 2),
                }
    except Exception as e:
        duration = (time.perf_counter() - start) * 1000.0
        crud.record_check(db, site.id, False, None, duration)
        return {
            "url": site.url,
            "online": False,
            "status_code": None,
            "response_time_ms": round(duration, 2),
            "error": str(e),
        }

@app.get("/history/{site_id}", response_model=list[CheckOut])
def get_check_history(site_id: int, db: Session = Depends(get_db)):
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    return (
        db.query(site.__class__.checks.property.mapper.class_)
        .filter_by(site_id=site_id)
        .order_by(site.__class__.checks.property.mapper.class_.checked_at.desc())
        .limit(20)
        .all()
    )
