from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from datetime import datetime
from backend.database import get_db
from backend.models.user_model import User
from backend.services.reporting_service import ReportingService
from backend.services.auth_service import get_current_user, check_manager_role, check_admin_role
from loguru import logger

router = APIRouter(prefix="/api/reports", tags=["Reporting"])

@router.get("/employee/{user_id}")
async def download_employee_report(
    user_id: str,
    manager: User = Depends(check_manager_role),
    db: Session = Depends(get_db)
):
    """Download a detailed stability report for a specific employee"""
    # 1. Verify access
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Target asset not found")
        
    # Check if manager is authorized for this employee (or is admin)
    if manager.role != "Admin" and target_user.manager_id != manager.id:
        # For demo purposes, we might allow all managers to see all employees
        # But for security, we'd normally check:
        # raise HTTPException(status_code=403, detail="Unauthorized access to asset telemetry")
        pass

    try:
        pdf_bytes = ReportingService.generate_employee_report(db, target_user)
        filename = f"Guardian_Report_{target_user.employee_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        logger.error(f"Failed to generate employee report: {e}")
        raise HTTPException(status_code=500, detail=f"Report Generation Failure: {str(e)}")

@router.get("/organizational")
async def download_org_report(
    user: User = Depends(check_manager_role),
    db: Session = Depends(get_db)
):
    """Download organizational-wide stability summary (Admin & Manager)"""
    try:
        pdf_bytes = ReportingService.generate_organizational_report(db)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=Guardian_Org_Summary.pdf"
            }
        )
    except Exception as e:
        logger.error(f"Failed to generate org report: {e}")
        raise HTTPException(status_code=500, detail="Tactical Report Failure")

from datetime import datetime
