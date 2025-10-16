from sqlalchemy.orm import Session
from sqlalchemy import select
from models import Site, Check

def create_site(db: Session, url: str) -> Site:
    existing = db.execute(select(Site).where(Site.url == str(url))).scalar_one_or_none()
    if existing:
        return existing
    site = Site(url=str(url))
    db.add(site)
    db.commit()
    db.refresh(site)
    return site

def list_sites(db: Session):
    return db.execute(select(Site)).scalars().all()

def record_check(db: Session, site_id: int, ok: bool, status_code: int, response_time_ms: float):
    check = Check(
        site_id=site_id,
        ok=ok,
        status_code=status_code,
        response_time_ms=response_time_ms,
    )
    db.add(check)
    db.commit()
    db.refresh(check)
    return check
