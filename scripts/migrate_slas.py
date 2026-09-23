from backend.db.session import engine
from sqlalchemy import text

statements = [
    "ALTER TABLE slas ADD COLUMN IF NOT EXISTS priority VARCHAR(10) DEFAULT 'P3' NOT NULL;",
    "ALTER TABLE slas ADD COLUMN IF NOT EXISTS target_response_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL;",
    "ALTER TABLE slas ADD COLUMN IF NOT EXISTS target_resolve_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() + INTERVAL '72 hours' NOT NULL;",
    "ALTER TABLE slas ADD COLUMN IF NOT EXISTS response_breached BOOLEAN DEFAULT FALSE NOT NULL;",
    "ALTER TABLE slas ADD COLUMN IF NOT EXISTS resolve_breached BOOLEAN DEFAULT FALSE NOT NULL;",
    "ALTER TABLE slas ADD COLUMN IF NOT EXISTS paused_reason VARCHAR(255);",
]

with engine.begin() as conn:
    for stmt in statements:
        print("Executing:", stmt)
        try:
            conn.execute(text(stmt))
            print("OK!")
        except Exception as e:
            print("Error/Warning:", e)

    try:
        conn.execute(text("UPDATE slas SET target_response_at = response_deadline WHERE response_deadline IS NOT NULL;"))
        conn.execute(text("UPDATE slas SET target_resolve_at = resolution_deadline WHERE resolution_deadline IS NOT NULL;"))
        conn.execute(text("UPDATE slas SET response_breached = is_response_breached WHERE is_response_breached IS NOT NULL;"))
        conn.execute(text("UPDATE slas SET resolve_breached = is_resolution_breached WHERE is_resolution_breached IS NOT NULL;"))
        print("Backfilled old column values successfully!")
    except Exception as e:
        print("Backfill note:", e)

print("Migration completed!")
