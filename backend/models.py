from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Site(Base):
    __tablename__ = "sites"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    checks = relationship("Check", back_populates="site", cascade="all, delete-orphan")

class Check(Base):
    __tablename__ = "checks"
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"))
    ok = Column(Boolean, nullable=False)
    status_code = Column(Integer, nullable=True)
    response_time_ms = Column(Float, nullable=True)
    checked_at = Column(DateTime, default=datetime.utcnow)
    site = relationship("Site", back_populates="checks")
