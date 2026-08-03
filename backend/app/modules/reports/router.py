from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.schemas import SuccessResponse
from app.modules.auth.dependencies import get_db, get_current_user
from app.modules.auth.models import User
from app.modules.reports.schemas import ReportSummary, ReportTemplate

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/summary", response_model=SuccessResponse[ReportSummary])
async def get_reports_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return SuccessResponse(
        message="Reports summary retrieved",
        data=ReportSummary(
            total_generated=48,
            scheduled=6,
            compliance_score=98.4,
            last_generated="2026-07-30 21:00:00 UTC",
        ),
    )

@router.get("/templates", response_model=SuccessResponse[List[ReportTemplate]])
async def get_report_templates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    templates = [
        ReportTemplate(id="sec-audit", name="Executive Security Audit", category="Security", description="High-level threat and incident executive brief", format="PDF"),
        ReportTemplate(id="compliance", name="PCI-DSS / ISO27001 Compliance", category="Compliance", description="Regulatory framework control validation", format="PDF/CSV"),
        ReportTemplate(id="inventory", name="Endpoint Hardware & Software Inventory", category="Asset", description="Full asset telemetry and software list", format="CSV/Excel"),
        ReportTemplate(id="command-log", name="Remote Command Audit Log Report", category="Audit", description="Detailed history of executed console commands", format="CSV"),
    ]
    return SuccessResponse(message="Report templates retrieved", data=templates)
