from pydantic import BaseModel
from typing import List, Dict, Any

class ReportSummary(BaseModel):
    total_generated: int
    scheduled: int
    compliance_score: float
    last_generated: str

class ReportTemplate(BaseModel):
    id: str
    name: str
    category: str
    description: str
    format: str
