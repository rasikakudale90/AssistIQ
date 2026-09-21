from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


TimeWindow = Literal["7d", "30d", "90d", "all"]


class SLAPerformanceMetrics(BaseModel):
    total_evaluated: int = 0
    response_breached_count: int = 0
    resolve_breached_count: int = 0
    compliance_rate_percent: float = 100.0


class TeamMetricItem(BaseModel):
    team_id: str
    team_name: str
    assigned_count: int = 0
    resolved_count: int = 0
    breach_count: int = 0
    avg_resolution_hours: float = 0.0
    avg_resolution_minutes: float = 0.0


class OperationalInsightsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    time_window: str
    total_cases: int
    open_cases: int
    resolved_cases: int
    closed_cases: int
    reopened_cases: int
    reopen_rate_percent: float
    avg_first_response_hours: Optional[float] = None
    avg_first_response_minutes: Optional[float] = None
    avg_resolution_hours: Optional[float] = None
    avg_resolution_minutes: Optional[float] = None
    sla_compliance_rate_percent: float = 100.0
    response_compliance_rate_percent: float = 100.0
    resolve_compliance_rate_percent: float = 100.0

    # Categorical Breakdowns
    cases_by_status: Dict[str, int] = Field(default_factory=dict)
    cases_by_priority: Dict[str, int] = Field(default_factory=dict)
    cases_by_type: Dict[str, int] = Field(default_factory=dict)
    cases_by_category: Dict[str, int] = Field(default_factory=dict)
    cases_by_site: Dict[str, int] = Field(default_factory=dict)
    cases_by_team: Dict[str, int] = Field(default_factory=dict)
    team_metrics: List[TeamMetricItem] = Field(default_factory=list)

    sla_metrics: SLAPerformanceMetrics
    ai_narration: Optional[str] = None
    ai_narrative: Optional[str] = None



class QuickDashboardStats(BaseModel):
    total_open_cases: int
    unassigned_cases: int
    high_critical_risk_cases: int
    active_sla_breaches: int
    cases_needing_review: int
