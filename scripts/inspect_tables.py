import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.db.session import engine
from sqlalchemy import text

with engine.connect() as conn:
    res = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"))
    print("Tables in public schema:")
    for r in res:
        print(" -", r[0])

    for tbl in ['ai_triage_results', 'case_summaries', 'case_risk_assessments', 'communication_drafts', 'escalation_events', 'knowledge_articles']:
        print(f"\nColumns in {tbl}:")
        res = conn.execute(text(f"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = '{tbl}' ORDER BY ordinal_position;"))
        for r in res:
            print(f"   {r[0]}: {r[1]} (nullable={r[2]})")
