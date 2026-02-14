"""Migration 002: Create reminders table.

Creates the reminders table for Phase 5 reminder support:
- id: UUID primary key
- task_id: Foreign key to tasks
- user_id: Foreign key to users
- remind_at: When to trigger the reminder
- notified: Idempotency flag to prevent duplicates
- created_at: Record creation timestamp

Run manually:
    psql $DATABASE_URL -f migrations/versions/002_create_reminders_table.sql

Or via Python:
    python migrations/versions/002_create_reminders_table.py
"""

UPGRADE_SQL = """
-- Create reminders table
CREATE TABLE IF NOT EXISTS reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    remind_at TIMESTAMP NOT NULL,
    notified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT fk_reminder_task FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    CONSTRAINT fk_reminder_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Add indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_reminders_task_id ON reminders (task_id);
CREATE INDEX IF NOT EXISTS idx_reminders_user_id ON reminders (user_id);
CREATE INDEX IF NOT EXISTS idx_reminders_remind_at ON reminders (remind_at);
CREATE INDEX IF NOT EXISTS idx_reminders_pending ON reminders (remind_at) WHERE notified = FALSE;
"""

DOWNGRADE_SQL = """
DROP TABLE IF EXISTS reminders;
"""


def upgrade(connection):
    """Apply migration."""
    connection.execute(UPGRADE_SQL)


def downgrade(connection):
    """Rollback migration."""
    connection.execute(DOWNGRADE_SQL)


if __name__ == "__main__":
    import os
    import psycopg2

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL not set")
        exit(1)

    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(UPGRADE_SQL)
    print("Migration 002 applied: reminders table created")
    cur.close()
    conn.close()
