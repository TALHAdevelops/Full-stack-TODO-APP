"""Migration 001: Add recurring task fields to tasks table.

Adds columns for Phase 5 recurring task support:
- due_date: Optional timestamp for task deadlines
- recurrence_rule: RRULE format string (e.g., FREQ=DAILY)
- is_recurring: Boolean flag for recurring tasks
- next_occurrence: Next scheduled spawn time

Run manually:
    psql $DATABASE_URL -f migrations/versions/001_add_recurring_fields.sql

Or via Python:
    python migrations/versions/001_add_recurring_fields.py
"""

UPGRADE_SQL = """
-- Add recurring task fields to tasks table
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_date TIMESTAMP;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS recurrence_rule TEXT;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN DEFAULT FALSE;
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS next_occurrence TIMESTAMP;

-- Add indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks (due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_is_recurring ON tasks (is_recurring);
CREATE INDEX IF NOT EXISTS idx_tasks_next_occurrence ON tasks (next_occurrence);
"""

DOWNGRADE_SQL = """
-- Remove indexes
DROP INDEX IF EXISTS idx_tasks_next_occurrence;
DROP INDEX IF EXISTS idx_tasks_is_recurring;
DROP INDEX IF EXISTS idx_tasks_due_date;

-- Remove columns
ALTER TABLE tasks DROP COLUMN IF EXISTS next_occurrence;
ALTER TABLE tasks DROP COLUMN IF EXISTS is_recurring;
ALTER TABLE tasks DROP COLUMN IF EXISTS recurrence_rule;
ALTER TABLE tasks DROP COLUMN IF EXISTS due_date;
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
    print("Migration 001 applied: recurring fields added to tasks table")
    cur.close()
    conn.close()
