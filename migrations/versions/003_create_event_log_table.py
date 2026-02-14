"""Migration 003: Create event_log table.

Creates the event_log table for Phase 5 audit trail support:
- Stores all task events immutably
- Supports replay and querying by user, type, time range, aggregate

Run manually:
    psql $DATABASE_URL -f migrations/versions/003_create_event_log_table.sql

Or via Python:
    python migrations/versions/003_create_event_log_table.py
"""

UPGRADE_SQL = """
-- Create event_log table for immutable audit trail
CREATE TABLE IF NOT EXISTS event_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id VARCHAR NOT NULL,
    event_type VARCHAR NOT NULL,
    user_id VARCHAR NOT NULL,
    aggregate_id VARCHAR NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    correlation_id VARCHAR DEFAULT '',
    data TEXT DEFAULT '{}',
    version INTEGER DEFAULT 1
);

-- Add indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_event_log_event_id ON event_log (event_id);
CREATE INDEX IF NOT EXISTS idx_event_log_event_type ON event_log (event_type);
CREATE INDEX IF NOT EXISTS idx_event_log_user_id ON event_log (user_id);
CREATE INDEX IF NOT EXISTS idx_event_log_aggregate_id ON event_log (aggregate_id);
CREATE INDEX IF NOT EXISTS idx_event_log_timestamp ON event_log (timestamp);
CREATE INDEX IF NOT EXISTS idx_event_log_user_time ON event_log (user_id, timestamp);
"""

DOWNGRADE_SQL = """
DROP TABLE IF EXISTS event_log;
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
    print("Migration 003 applied: event_log table created")
    cur.close()
    conn.close()
