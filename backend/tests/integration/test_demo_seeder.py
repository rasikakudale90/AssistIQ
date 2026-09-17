from sqlalchemy.orm import Session
from backend.models import User, Team, Case, SLA, KnowledgeArticle, AITriageResult
from scripts.seed_demo_data import seed_demo_data


def test_seed_demo_data_execution(db_session: Session):
    # Run seeder against test db
    seed_demo_data(db_session)

    # 1. Verify Users (all 5 roles created)
    users = db_session.query(User).all()
    roles = {u.role.value for u in users}
    assert "Requester" in roles
    assert "Operator" in roles
    assert "TeamLead" in roles
    assert "Manager" in roles
    assert "Administrator" in roles

    # 2. Verify Teams
    teams = db_session.query(Team).all()
    assert len(teams) >= 3

    # 3. Verify Cases (18 seeded cases)
    cases = db_session.query(Case).all()
    assert len(cases) >= 18

    # 4. Verify SLAs
    slas = db_session.query(SLA).all()
    assert len(slas) >= 18

    # 5. Verify Knowledge Base Articles
    kbs = db_session.query(KnowledgeArticle).all()
    assert len(kbs) >= 4

    # 6. Verify AI Triage Results
    triages = db_session.query(AITriageResult).all()
    assert len(triages) >= 18
