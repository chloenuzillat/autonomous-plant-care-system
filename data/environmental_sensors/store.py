import sqlite3
from contextlib import closing
from data.config import DB_PATH
#SQL Queries
# plant_info is GLOBAL species reference data: the care ranges every plant of
# that species wants, shared by all of them and sourced from an external API.
# It says nothing about any one houseplant, so it carries no position and no
# readings. Its local counterpart is user_plant_log.
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

# user_plant_log is LOCAL measured data: what this robot actually recorded in
# this user's home, at one spot, at one moment. Nothing in it generalises to
# other homes or to other plants of the same species -- it is the counterpart to
# the global ranges in plant_info, and the two are compared to judge whether a
# spot suits a plant.
#
# A reading carries two ids, because the user can own several plants of the same
# species: user_plant_id names the individual pot the reading came from, and
# plant_id names its species, which is what plant_info is keyed by. Readings are
# grouped by user_plant_id; ranges are looked up by plant_id.
#
# Positions are measured to the centre of the robot, in whatever floor plan it is
# navigating: the simulation's grid today, a real room map later. This table
# stores poses without judging them -- deciding which poses are reachable belongs
# to the robot that produced them, not to the log that records them.
#
# lux/temp/humidity are ambient: they describe the spot, so any plant standing
# there would read the same. soil_moisture_pct is not -- it describes the inside
# of this plant's pot and mostly reflects when it was last watered, so it drives
# watering decisions rather than placement decisions.
CREATE_USER_PLANT_LOG_TABLE = """
CREATE TABLE IF NOT EXISTS user_plant_log (
    log_id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_plant_id           INTEGER NOT NULL,   -- which of the user's plants
    plant_id                INTEGER NOT NULL,   -- what species it is
    lux_reading             REAL,       
    temp_reading            REAL,       
    humidity_reading        REAL,      
    soil_moisture_pct       REAL,       -- in this plant's pot, not the room
    pos_x                   REAL,       -- position of the robot stood for this reading
    pos_y                   REAL,
    heading_deg             REAL,       -- robot's orientation in the room w/ respect to the x'axis at the time of reading.
    time_stamp              TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY(plant_id) REFERENCES plant_info(plant_id),

    CHECK (heading_deg IS NULL OR heading_deg >= 0 AND heading_deg < 360),
    CHECK (soil_moisture_pct IS NULL OR soil_moisture_pct BETWEEN 0 AND 100)

);
"""

# Every read filters by plant and sorts by time, so index that pair.
CREATE_USER_PLANT_LOG_INDEX = """
CREATE INDEX IF NOT EXISTS idx_user_plant_log_user_plant_time
ON user_plant_log (user_plant_id, time_stamp);
"""

# Spatial lookups scan a bounding box before measuring distance, so index the box.
CREATE_USER_PLANT_LOG_POS_INDEX = """
CREATE INDEX IF NOT EXISTS idx_user_plant_log_pos
ON user_plant_log (pos_x, pos_y);
"""

UPSERT_PLANT_INFO = """
INSERT INTO plant_info (plant_id, plant_name, lux_min, lux_max,
                        temp_min_celsius, temp_max_celsius,
                        humidity_min_pct, humidity_max_pct,
                        source, last_updated)
VALUES (:plant_id, :plant_name, :lux_min, :lux_max,
        :temp_min_celsius, :temp_max_celsius,
        :humidity_min_pct, :humidity_max_pct,
        :source, datetime('now'))
ON CONFLICT(plant_id) DO UPDATE SET
    plant_name       = excluded.plant_name,
    lux_min          = excluded.lux_min,
    lux_max          = excluded.lux_max,
    temp_min_celsius = excluded.temp_min_celsius,
    temp_max_celsius = excluded.temp_max_celsius,
    humidity_min_pct = excluded.humidity_min_pct,
    humidity_max_pct = excluded.humidity_max_pct,
    source           = excluded.source,
    last_updated     = datetime('now');
"""

SELECT_PLANT_INFO = """
SELECT *
FROM plant_info
WHERE plant_id = :plant_id;
"""

INSERT_USER_PLANT_LOG = """
INSERT INTO user_plant_log (user_plant_id, plant_id, lux_reading, temp_reading, humidity_reading,
                            soil_moisture_pct, pos_x, pos_y, heading_deg, time_stamp)
VALUES (:user_plant_id, :plant_id, :lux_reading, :temp_reading, :humidity_reading,
        :soil_moisture_pct, :pos_x, :pos_y, :heading_deg,
        COALESCE(:time_stamp, datetime('now')));
"""

SELECT_LATEST_USER_PLANT_LOG = """
SELECT log_id, user_plant_id, plant_id, lux_reading, temp_reading, humidity_reading,
       soil_moisture_pct, pos_x, pos_y, heading_deg, time_stamp
FROM user_plant_log
WHERE user_plant_id = :user_plant_id
ORDER BY time_stamp DESC, log_id DESC
LIMIT 1;
"""

SELECT_USER_PLANT_LOGS = """
SELECT log_id, user_plant_id, plant_id, lux_reading, temp_reading, humidity_reading,
       soil_moisture_pct, pos_x, pos_y, heading_deg, time_stamp
FROM user_plant_log
WHERE user_plant_id = :user_plant_id
ORDER BY time_stamp DESC, log_id DESC
LIMIT :limit;
"""

# Readings taken anywhere near a point, regardless of which plant they belong to.
SELECT_USER_LOGS_NEAR_POSITION = """
SELECT log_id, user_plant_id, plant_id, lux_reading, temp_reading, humidity_reading,
       soil_moisture_pct, pos_x, pos_y, heading_deg, time_stamp,
       ((pos_x - :pos_x) * (pos_x - :pos_x)
      + (pos_y - :pos_y) * (pos_y - :pos_y)) AS distance_squared
FROM user_plant_log
WHERE pos_x IS NOT NULL AND pos_y IS NOT NULL
  AND pos_x BETWEEN :pos_x - :radius AND :pos_x + :radius
  AND pos_y BETWEEN :pos_y - :radius AND :pos_y + :radius
  AND distance_squared <= :radius * :radius
ORDER BY distance_squared ASC, time_stamp DESC
LIMIT :limit;
"""

DELETE_USER_PLANT_LOG = """
DELETE FROM user_plant_log
WHERE user_plant_id = :user_plant_id;
"""

#CRUD Functions
# The log table used to be called plant_log, which read like species data.
RENAMED_TABLES = {"plant_log": "user_plant_log"}

# Columns added after the first release. CREATE TABLE IF NOT EXISTS is a no-op on
# an existing database, so older files need the columns bolted on by hand.
COLUMN_MIGRATIONS = {
    "user_plant_log": {
        "user_plant_id": "INTEGER",
        "pos_x": "REAL",
        "pos_y": "REAL",
        "heading_deg": "REAL",
        "soil_moisture_pct": "REAL",
    },
}


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    #True if `table` is present in this database.
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)
    ).fetchone()

    return row is not None


def _rename_old_tables(conn: sqlite3.Connection) -> None:
    #Rename tables that have since been renamed, before anything is created.
    for old_name, new_name in RENAMED_TABLES.items():
        if _table_exists(conn, old_name) and not _table_exists(conn, new_name):
            conn.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")


def _add_missing_columns(conn: sqlite3.Connection) -> None:
    #Add any columns an older database is missing.
    for table, columns in COLUMN_MIGRATIONS.items():
        existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
        for name, column_type in columns.items():
            if name not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {column_type}")


def init_db(db_path: str = DB_PATH) -> None:
    #Create the plant_info and user_plant_log tables if they don't exist.
    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            _rename_old_tables(conn)
            conn.execute(CREATE_PLANT_INFO)
            conn.execute(CREATE_USER_PLANT_LOG_TABLE)
            _add_missing_columns(conn)
            conn.execute(CREATE_USER_PLANT_LOG_INDEX)
            conn.execute(CREATE_USER_PLANT_LOG_POS_INDEX)

REQUIRED_USER_PLANT_LOG_KEYS = {"user_plant_id", "plant_id", "lux_reading", "temp_reading", "humidity_reading"}
OPTIONAL_USER_PLANT_LOG_KEYS = {"time_stamp", "soil_moisture_pct",
                                 "pos_x", "pos_y", "heading_deg"}

REQUIRED_PLANT_INFO_KEYS = {"plant_id", "plant_name"}
OPTIONAL_PLANT_INFO_KEYS = {
    "lux_min", "lux_max",
    "temp_min_celsius", "temp_max_celsius",
    "humidity_min_pct", "humidity_max_pct",
    "source",
}


def is_valid_soil_moisture(soil_moisture_pct) -> bool:
    #A soil moisture reading is valid when it is unset, or a percentage.
    if soil_moisture_pct is None:
        return True

    return 0.0 <= float(soil_moisture_pct) <= 100.0


def add_plant_info(db_path: str = DB_PATH, plant_record: dict = None) -> None:
    #Insert or update the global species reference row for plant_id.
    if not plant_record:
        return

    keys = set(plant_record)
    if not REQUIRED_PLANT_INFO_KEYS <= keys or not keys <= (REQUIRED_PLANT_INFO_KEYS | OPTIONAL_PLANT_INFO_KEYS):
        return

    row = {key: plant_record.get(key)
           for key in REQUIRED_PLANT_INFO_KEYS | OPTIONAL_PLANT_INFO_KEYS}

    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            conn.execute(UPSERT_PLANT_INFO, row)


def read_plant_info(plant_id: int, db_path: str = DB_PATH) -> dict:
    #Return the plant_info row for plant_id, or an empty dict if there isn't one.
    with closing(sqlite3.connect(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(SELECT_PLANT_INFO, {"plant_id": plant_id}).fetchone()

    return dict(row) if row else {}


def add_user_plant_log(db_path: str = DB_PATH, plant_record: dict = None) -> None:
    #Insert a single measured reading row into user_plant_log.
    if not plant_record:
        return

    keys = set(plant_record)
    if not REQUIRED_USER_PLANT_LOG_KEYS <= keys or not keys <= (REQUIRED_USER_PLANT_LOG_KEYS | OPTIONAL_USER_PLANT_LOG_KEYS):
        return

    row = {key: plant_record.get(key)
           for key in REQUIRED_USER_PLANT_LOG_KEYS | OPTIONAL_USER_PLANT_LOG_KEYS}

    if not is_valid_soil_moisture(row["soil_moisture_pct"]):
        return

    if row["heading_deg"] is not None:
        row["heading_deg"] = float(row["heading_deg"]) % 360

    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            conn.execute(INSERT_USER_PLANT_LOG, row)

def read_user_plant_log(user_plant_id: int, db_path: str = DB_PATH) -> dict:
    #Return the most recent reading for one of the user's plants, or an empty dict if there isn't one.
    with closing(sqlite3.connect(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(SELECT_LATEST_USER_PLANT_LOG,
                           {"user_plant_id": user_plant_id}).fetchone()

    return dict(row) if row else {}

def read_user_plant_logs(user_plant_id: int, db_path: str = DB_PATH, limit: int = 100) -> list:
    #Return up to `limit` readings for one of the user's plants, newest first.
    with closing(sqlite3.connect(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(SELECT_USER_PLANT_LOGS,
                            {"user_plant_id": user_plant_id, "limit": limit}).fetchall()

    return [dict(row) for row in rows]

def read_user_logs_near(pos_x: float, pos_y: float, radius: float = 50.0,
                         db_path: str = DB_PATH, limit: int = 100) -> list:
    #Return readings taken within `radius` cells of (pos_x, pos_y), nearest first.
    with closing(sqlite3.connect(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(SELECT_USER_LOGS_NEAR_POSITION,
                            {"pos_x": pos_x, "pos_y": pos_y,
                             "radius": radius, "limit": limit}).fetchall()

    return [dict(row) for row in rows]

def delete_user_plant_log(user_plant_id: int, db_path: str = DB_PATH) -> list:
    #Delete every reading for one of the user's plants and return them, or [] if there was nothing to delete.
    with closing(sqlite3.connect(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        with conn:
            rows = conn.execute(SELECT_USER_PLANT_LOGS,
                                {"user_plant_id": user_plant_id, "limit": -1}).fetchall()
            if not rows:
                return []
            conn.execute(DELETE_USER_PLANT_LOG, {"user_plant_id": user_plant_id})

    return [dict(row) for row in rows]
