import sqlite3
from contextlib import closing
from pathlib import Path
from read_arduino.config import DB_PATH

#SQL Queries
CREATE_PLANT_INFO = """
CREATE TABLE IF NOT EXISTS plant_info (
    plant_id                INTEGER PRIMARY KEY,
    plant_name              TEXT NOT NULL,
    lux_min                 REAL,
    lux_max                 REAL,
    temp_min_celsius        REAL,
    temp_max_celsius        REAL,
    humidity_min_pct        REAL,
    humidity_max_pct        REAL,
    source                  TEXT,       -- e.g. 'perenual', 'trefle', 'manual'
    last_updated            TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

CREATE_PLANT_LOG_TABLE = """
CREATE TABLE IF NOT EXISTS plant_log (
    log_id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    plant_id                INTEGER NOT NULL,
    lux_reading             REAL,
    temp_reading            REAL,
    humidity_reading        REAL,
    time_stamp              TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY(plant_id) REFERENCES plant_info(plant_id)

);
"""

# Every read filters by plant and sorts by time, so index that pair.
CREATE_PLANT_LOG_INDEX = """
CREATE INDEX IF NOT EXISTS idx_plant_log_plant_time
ON plant_log (plant_id, time_stamp);
"""

INSERT_PLANT_LOG = """
INSERT INTO plant_log (plant_id, lux_reading, temp_reading, humidity_reading, time_stamp)
VALUES (:plant_id, :lux_reading, :temp_reading, :humidity_reading,
        COALESCE(:time_stamp, datetime('now')));
"""

SELECT_LATEST_PLANT_LOG = """
SELECT log_id, plant_id, lux_reading, temp_reading, humidity_reading, time_stamp
FROM plant_log
WHERE plant_id = :plant_id
ORDER BY time_stamp DESC, log_id DESC
LIMIT 1;
"""

SELECT_PLANT_LOGS = """
SELECT log_id, plant_id, lux_reading, temp_reading, humidity_reading, time_stamp
FROM plant_log
WHERE plant_id = :plant_id
ORDER BY time_stamp DESC, log_id DESC
LIMIT :limit;
"""

DELETE_PLANT_LOG = """
DELETE FROM plant_log
WHERE plant_id = :plant_id;
"""

#CRUD Functions
def init_db(db_path: str = DB_PATH) -> None:
    """Create the plant_info table and plant_log table if they don't exist."""
    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            conn.execute(CREATE_PLANT_INFO)
            conn.execute(CREATE_PLANT_LOG_TABLE)
            conn.execute(CREATE_PLANT_LOG_INDEX)

REQUIRED_PLANT_LOG_KEYS = {"plant_id", "lux_reading", "temp_reading", "humidity_reading"}
OPTIONAL_PLANT_LOG_KEYS = {"time_stamp"}




def add_plant_log(db_path: str = DB_PATH, plant_record: dict = None) -> None:
    #Insert a single sensor reading row into plant_log.
    if not plant_record:
        return

    keys = set(plant_record)
    if not REQUIRED_PLANT_LOG_KEYS <= keys or not keys <= (REQUIRED_PLANT_LOG_KEYS | OPTIONAL_PLANT_LOG_KEYS):
        return

    row = {key: plant_record.get(key) for key in REQUIRED_PLANT_LOG_KEYS | OPTIONAL_PLANT_LOG_KEYS}

    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            conn.execute(INSERT_PLANT_LOG, row)

def read_plant_log(plant_id: int, db_path: str = DB_PATH) -> dict:
    #Return the most recent plant_log row for plant_id, or an empty dict if there isn't one.
    with closing(sqlite3.connect(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(SELECT_LATEST_PLANT_LOG, {"plant_id": plant_id}).fetchone()

    return dict(row) if row else {}

def read_plant_logs(plant_id: int, db_path: str = DB_PATH, limit: int = 100) -> list:
    #Return up to `limit` plant_log rows for plant_id, newest first.
    with closing(sqlite3.connect(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(SELECT_PLANT_LOGS, {"plant_id": plant_id, "limit": limit}).fetchall()

    return [dict(row) for row in rows]

def delete_plant_log(plant_id: int, db_path: str = DB_PATH) -> list:
    #Delete every plant_log row for plant_id and return them, or [] if there was nothing to delete.
    with closing(sqlite3.connect(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        with conn:
            rows = conn.execute(SELECT_PLANT_LOGS,
                                {"plant_id": plant_id, "limit": -1}).fetchall()
            if not rows:
                return []
            conn.execute(DELETE_PLANT_LOG, {"plant_id": plant_id})

    return [dict(row) for row in rows]
