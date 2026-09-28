import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.db.session import engine
from sqlalchemy import text

def run_migration():
    print("Running AI tables schema migration on Supabase PostgreSQL...")
    with engine.connect() as conn:
        with conn.begin():
            # 1. ai_triage_results
            print("Migrating ai_triage_results...")
            conn.execute(text("""
                ALTER TABLE ai_triage_results 
                    ADD COLUMN IF NOT EXISTS suggested_category VARCHAR(100),
                    ADD COLUMN IF NOT EXISTS suggested_severity VARCHAR(50),
                    ADD COLUMN IF NOT EXISTS supporting_factors JSON DEFAULT '[]'::json,
                    ADD COLUMN IF NOT EXISTS missing_info JSON DEFAULT '[]'::json,
                    ADD COLUMN IF NOT EXISTS suggested_team VARCHAR(100),
                    ADD COLUMN IF NOT EXISTS recommended_next_action TEXT,
                    ADD COLUMN IF NOT EXISTS related_case_ids JSON DEFAULT '[]'::json;
            """))
            # Make legacy columns nullable if they had NOT NULL constraints
            conn.execute(text("""
                ALTER TABLE ai_triage_results 
                    ALTER COLUMN confidence_score DROP NOT NULL,
                    ALTER COLUMN confidence_level DROP NOT NULL;
            """))
            # Copy reasoning into recommended_next_action if present
            conn.execute(text("""
                UPDATE ai_triage_results 
                SET recommended_next_action = reasoning 
                WHERE recommended_next_action IS NULL AND reasoning IS NOT NULL;
            """))
            # Update default for supporting_factors, missing_info, related_case_ids
            conn.execute(text("""
                UPDATE ai_triage_results SET supporting_factors = '[]'::json WHERE supporting_factors IS NULL;
                UPDATE ai_triage_results SET missing_info = '[]'::json WHERE missing_info IS NULL;
                UPDATE ai_triage_results SET related_case_ids = '[]'::json WHERE related_case_ids IS NULL;
            """))

            # 2. case_summaries
            print("Migrating case_summaries...")
            conn.execute(text("""
                ALTER TABLE case_summaries 
                    ADD COLUMN IF NOT EXISTS last_source_message_id VARCHAR(36),
                    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();
            """))
            conn.execute(text("""
                ALTER TABLE case_summaries 
                    ALTER COLUMN model_version DROP NOT NULL;
            """))

            # 3. case_risk_assessments
            print("Migrating case_risk_assessments...")
            conn.execute(text("""
                ALTER TABLE case_risk_assessments 
                    ADD COLUMN IF NOT EXISTS signals JSON DEFAULT '{}'::json,
                    ADD COLUMN IF NOT EXISTS computed_at TIMESTAMPTZ DEFAULT NOW();
            """))
            conn.execute(text("""
                ALTER TABLE case_risk_assessments 
                    ALTER COLUMN risk_score DROP NOT NULL,
                    ALTER COLUMN factors DROP NOT NULL,
                    ALTER COLUMN assessed_at DROP NOT NULL;
            """))
            conn.execute(text("""
                UPDATE case_risk_assessments SET signals = '{}'::json WHERE signals IS NULL;
            """))

            # 4. escalation_events
            print("Migrating escalation_events...")
            conn.execute(text("""
                ALTER TABLE escalation_events 
                    ADD COLUMN IF NOT EXISTS trigger_reason VARCHAR(50) DEFAULT 'sla_warning',
                    ADD COLUMN IF NOT EXISTS escalated_to VARCHAR(36),
                    ADD COLUMN IF NOT EXISTS escalated_by VARCHAR(36) DEFAULT 'system';
            """))
            conn.execute(text("""
                ALTER TABLE escalation_events 
                    ALTER COLUMN escalated_by_id DROP NOT NULL,
                    ALTER COLUMN previous_level DROP NOT NULL,
                    ALTER COLUMN new_level DROP NOT NULL,
                    ALTER COLUMN reason DROP NOT NULL;
            """))

            # 5. communication_drafts
            print("Migrating communication_drafts...")
            conn.execute(text("""
                ALTER TABLE communication_drafts 
                    ADD COLUMN IF NOT EXISTS body TEXT,
                    ADD COLUMN IF NOT EXISTS reviewed_by VARCHAR(36),
                    ADD COLUMN IF NOT EXISTS sent_message_id VARCHAR(36);
            """))
            conn.execute(text("""
                UPDATE communication_drafts SET body = draft_text WHERE body IS NULL AND draft_text IS NOT NULL;
                UPDATE communication_drafts SET body = 'Generated draft' WHERE body IS NULL;
            """))
            conn.execute(text("""
                ALTER TABLE communication_drafts ALTER COLUMN body SET NOT NULL;
            """))

    print("AI tables schema migration completed successfully!")

if __name__ == "__main__":
    run_migration()
