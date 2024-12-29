from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    reports = relationship("ThreatReport", back_populates="reporter")
    scan_history = relationship("ScanHistory", back_populates="user")

class ThreatReport(Base):
    __tablename__ = "threat_reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"))
    threat_type = Column(String)  # phishing, malware, deepfake, etc.
    url = Column(String, nullable=True)
    description = Column(String)
    evidence = Column(JSON)  # Store additional evidence like screenshots
    status = Column(String)  # pending, verified, false_positive
    created_at = Column(DateTime, default=datetime.utcnow)
    
    reporter = relationship("User", back_populates="reports")

class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    scan_type = Column(String)  # url, file, media
    target = Column(String)  # URL or filename
    threat_level = Column(Float)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="scan_history")

class DeepFakeAnalysis(Base):
    __tablename__ = "deepfake_analysis"

    id = Column(Integer, primary_key=True, index=True)
    file_hash = Column(String, unique=True, index=True)
    is_fake = Column(Boolean)
    confidence = Column(Float)
    analysis_details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class CommunityDatabase(Base):
    __tablename__ = "community_database"

    id = Column(Integer, primary_key=True, index=True)
    threat_type = Column(String)
    indicator = Column(String)  # URL, domain, file hash, etc.
    confidence = Column(Float)
    reports_count = Column(Integer, default=1)
    last_reported = Column(DateTime, default=datetime.utcnow)
    status = Column(String)  # active, resolved, false_positive
