from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings

Base = declarative_base()

class Report(Base):
    __tablename__ = "community_reports"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)  # 'phishing', 'spam', 'deepfake', etc.
    url = Column(String, nullable=True)
    content = Column(String, nullable=True)
    reporter_id = Column(String, index=True)
    status = Column(String, default="pending")  # pending, verified, false_positive
    risk_score = Column(Float, default=0.0)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    verified_count = Column(Integer, default=0)
    false_positive_count = Column(Integer, default=0)

class CommunityReportingService:
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    async def submit_report(self, report_data: Dict) -> Dict:
        """Submit a new community report"""
        db = self.SessionLocal()
        try:
            report = Report(
                type=report_data.get("type"),
                url=report_data.get("url"),
                content=report_data.get("content"),
                reporter_id=report_data.get("reporter_id"),
                details=report_data.get("details", {})
            )
            db.add(report)
            db.commit()
            db.refresh(report)
            
            # Trigger automatic analysis
            analysis_result = await self._analyze_report(report)
            if analysis_result["risk_score"] > 0.8:
                report.status = "verified"
                report.risk_score = analysis_result["risk_score"]
                db.commit()
            
            return {
                "report_id": report.id,
                "status": report.status,
                "risk_score": report.risk_score,
                "analysis": analysis_result
            }
        finally:
            db.close()

    async def verify_report(self, report_id: int, verifier_id: str, is_valid: bool) -> Dict:
        """Verify or mark a report as false positive"""
        db = self.SessionLocal()
        try:
            report = db.query(Report).filter(Report.id == report_id).first()
            if not report:
                return {"error": "Report not found"}

            if is_valid:
                report.verified_count += 1
                if report.verified_count >= 3:  # Threshold for verification
                    report.status = "verified"
            else:
                report.false_positive_count += 1
                if report.false_positive_count >= 3:  # Threshold for false positive
                    report.status = "false_positive"

            db.commit()
            return {
                "report_id": report.id,
                "status": report.status,
                "verified_count": report.verified_count,
                "false_positive_count": report.false_positive_count
            }
        finally:
            db.close()

    async def get_reports(self, 
                         status: Optional[str] = None, 
                         report_type: Optional[str] = None,
                         limit: int = 10) -> List[Dict]:
        """Get community reports with optional filters"""
        db = self.SessionLocal()
        try:
            query = db.query(Report)
            if status:
                query = query.filter(Report.status == status)
            if report_type:
                query = query.filter(Report.type == report_type)
            
            reports = query.order_by(Report.created_at.desc()).limit(limit).all()
            return [{
                "id": report.id,
                "type": report.type,
                "url": report.url,
                "status": report.status,
                "risk_score": report.risk_score,
                "created_at": report.created_at.isoformat(),
                "verified_count": report.verified_count,
                "false_positive_count": report.false_positive_count
            } for report in reports]
        finally:
            db.close()

    async def get_report_stats(self) -> Dict:
        """Get statistics about community reports"""
        db = self.SessionLocal()
        try:
            total_reports = db.query(Report).count()
            verified_reports = db.query(Report).filter(Report.status == "verified").count()
            false_positives = db.query(Report).filter(Report.status == "false_positive").count()
            pending_reports = db.query(Report).filter(Report.status == "pending").count()

            return {
                "total_reports": total_reports,
                "verified_reports": verified_reports,
                "false_positives": false_positives,
                "pending_reports": pending_reports,
                "verification_rate": (verified_reports / total_reports) if total_reports > 0 else 0,
                "false_positive_rate": (false_positives / total_reports) if total_reports > 0 else 0
            }
        finally:
            db.close()

    async def _analyze_report(self, report: Report) -> Dict:
        """Analyze a report using available services"""
        risk_score = 0.0
        analysis_details = {}

        try:
            if report.type == "phishing" and report.url:
                # Use threat analysis service
                from backend.app.services.threat_analysis import threat_analysis_service
                url_analysis = await threat_analysis_service.analyze_url(report.url)
                risk_score = max(risk_score, url_analysis.get("risk_score", 0))
                analysis_details["url_analysis"] = url_analysis

            elif report.type == "spam" and report.content:
                # Use spam detection service
                from backend.app.services.spam_detection import spam_detection_service
                spam_analysis = spam_detection_service.detect_spam(report.content)
                risk_score = max(risk_score, spam_analysis.get("spam_probability", 0))
                analysis_details["spam_analysis"] = spam_analysis

            elif report.type == "deepfake" and report.url:
                # Use deepfake detection service
                from backend.app.services.deepfake_detection import deepfake_detection_service
                deepfake_analysis = await deepfake_detection_service.analyze_image(report.url)
                risk_score = max(risk_score, deepfake_analysis.get("confidence", 0))
                analysis_details["deepfake_analysis"] = deepfake_analysis

        except Exception as e:
            analysis_details["error"] = str(e)

        return {
            "risk_score": risk_score,
            "details": analysis_details
        }

community_reporting_service = CommunityReportingService()
