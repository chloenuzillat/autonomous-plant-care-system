import sqlite3
from contextlib import closing
from pathlib import Path
from read_arduino.config import DB_PATH

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
    plant_id                INTEGER PRIMARY KEY,
    lux_reading             REAL,
    temp_reading            REAL,
    humidity_reading        REAL,
    time_stamp              TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY(plant_id) REFERENCES plant_info(plant_id)

);
"""
def init_db(db_path: str = DB_PATH) -> None:
    """Create the plant_info table and plant_log table if they don't exist."""
    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            conn.execute(CREATE_PLANT_INFO)
            conn.execute(CREATE_PLANT_LOG_TABLE)

def add_plant_log(db_path: str = DB_PATH, plant_log: dict = None) -> None:
    if(plant_log.keys() != ["plant_id", "lux_reading", "temp_reading", "humidity_reading", "time_stamp"]):
        return

    INSERT_PLANT_LOG = """
    INSERT INTO plant_log

    """
