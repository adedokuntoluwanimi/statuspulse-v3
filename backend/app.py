import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, List

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

DB_PATH = "/data/statuspulse.db"

@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL
        );
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_id INTEGER NOT NULL,
            ok INTEGER NOT NULL,
            status_code INTEGER,
            response_time_ms REAL,
            checked_at TEXT NOT NULL,
            FOREIGN KEY (site_id) REFERENCES sites(id) ON DELETE CASCADE
        );
        """)

app = FastAPI(title="StatusPulse API, lean")

class SiteCreate(BaseModel):
    url: HttpUrl

class SiteOut(BaseModel):
    id: int
    url: str
    created_at: datetime

class CheckOut(BaseModel):
    id: int
    site_id: int
    ok: bool
    status_code: Optional[int]
    response_time_ms: Optional[float]
    checked_at: datetime

@app.on_event("startup")
def startup():
    init_db()

@app.post("/sites", response_model=SiteOut)
def add_site(payload: SiteCreate):
    now = datetime.utcnow().isoformat()
    with db() as conn:
        # Upsert-like behavior, return existing if present
        row = conn.execute("SELECT * FROM sites WHERE url = ?", (str(payload.url),)).fetchone()
        if row:
            return SiteOut(id=row["id"], url=row["url"], created_at=datetime.fromisoformat(row["created_at"]))
        cur = conn.execute(
            "INSERT INTO sites (url, created_at) VALUES (?, ?)",
            (str(payload.url), now),
        )
        site_id = cur.lastrowid
        row = conn.execute("SELECT * FROM sites WHERE id = ?", (site_id,)).fetchone()
        return SiteOut(id=row["id"], url=row["url"], created_at=datetime.fromisoformat(row["created_at"]))

@app.get("/sites", response_model=List[SiteOut])
def list_sites():
    with db() as conn:
        rows = conn.execute("SELECT * FROM sites ORDER BY id DESC").fetchall()
        return [
            SiteOut(id=r["id"], url=r["url"], created_at=datetime.fromisoformat(r["created_at"]))
            for r in rows
        ]

@app.get("/status/{site_id}")
async def check_status(site_id: int):
    with db() as conn:
        site = conn.execute("SELECT * FROM sites WHERE id = ?", (site_id,)).fetchone()
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")

    url = site["url"]
    started = datetime.utcnow()
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            ok = 200 <= resp.status_code < 400
            status_code = resp.status_code
    except Exception as e:
        ok = False
        status_code = None

    duration_ms = (datetime.utcnow() - started).total_seconds() * 1000.0

    # persist check
    with db() as conn:
        conn.execute(
            "INSERT INTO checks (site_id, ok, status_code, response_time_ms, checked_at) VALUES (?, ?, ?, ?, ?)",
            (site_id, int(ok), status_code, duration_ms, datetime.utcnow().isoformat()),
        )

    return {
        "url": url,
        "online": ok,
        "status_code": status_code,
        "response_time_ms": round(duration_ms, 2),
    }

@app.get("/history/{site_id}", response_model=List[CheckOut])
def history(site_id: int):
    with db() as conn:
        site = conn.execute("SELECT 1 FROM sites WHERE id = ?", (site_id,)).fetchone()
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")
        rows = conn.execute(
            "SELECT * FROM checks WHERE site_id = ? ORDER BY checked_at DESC LIMIT 20",
            (site_id,),
        ).fetchall()
        return [
            CheckOut(
                id=r["id"],
                site_id=r["site_id"],
                ok=bool(r["ok"]),
                status_code=r["status_code"],
                response_time_ms=r["response_time_ms"],
                checked_at=datetime.fromisoformat(r["checked_at"]),
            )
            for r in rows
        ]

