from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel
from backend.db.session import check_db_health

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str = "ok"
    db: Literal["ok", "error"]


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check endpoint",
    description="Returns API status and database connectivity. Never invokes AI quotas.",
)
def get_health() -> HealthResponse:
    db_ok = check_db_health()
    return HealthResponse(
        status="ok",
        db="ok" if db_ok else "error",
    )
