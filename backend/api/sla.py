from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.core.errors import NotFoundException
from backend.db.session import get_db
from backend.models.user import User
from backend.models.sla import SLA
from backend.schemas.sla import SLAResponse
from backend.services.case_service import CaseService
from backend.services.sla_service import SLAService

router = APIRouter(tags=["SLA & Service Targets"])


@router.get("/cases/{case_id}/sla", response_model=SLAResponse)
def get_case_sla(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves SLA tracking information, 24/7 elapsed deadlines, and countdown status for a case (SRS §4.3).
    """
    case = CaseService.get_case(db, current_user, case_id)
    sla = db.query(SLA).filter(SLA.case_id == case.id).first()
    if not sla:
        # If no SLA record exists, create one lazily
        sla = SLAService.create_sla_for_case(db, case)
        db.commit()
        db.refresh(sla)

    return SLAService.build_sla_response(sla)


@router.post("/scheduler/sweep")
async def trigger_the_sweep(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Manually triggers 'The Sweep' background job on demand (SRS §4.3 & §5.7).
    """
    from backend.scheduler.sweep import run_the_sweep
    stats = await run_the_sweep(db=db)
    return {
        "status": "success",
        "message": "The Sweep executed successfully",
        "stats": stats,
    }
