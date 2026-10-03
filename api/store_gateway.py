"""The only place in the API that talks to the store.

Exists for two reasons:

* The store's writers take the database path as their *first* argument, while
  every reader takes it last. Route handlers should not have to remember that.
* The writers report failure by returning ``None`` -- the same thing they return
  on success. A route handler needs to know which happened, so every write here
  is confirmed by reading back and raising :class:`StoreRejected` if nothing
  landed.

Nothing in data/environmental_sensors/store.py is modified; Python-side code
keeps calling it directly.
"""

from pathlib import Path
from typing import List, Optional

from data.environmental_sensors import store


class StoreRejected(RuntimeError):
    """A write passed validation here but the store still did not take it."""


class StoreGateway:
    """Store access bound to one database file."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)

    def init(self) -> None:
        """Create the tables, and migrate an older file, if needed."""
        store.init_db(self.db_path)

    # -- species (global reference data) ----------------------------------

    def read_species(self, plant_id: int) -> dict:
        """
        :return: The plant_info row, or {} if this species is unknown
        """
        return store.read_plant_info(plant_id, self.db_path)

    def upsert_species(self, record: dict) -> dict:
        """
        Insert or update one species' care ranges.

        :param record: Keys matching plant_info, without last_updated
        :return: The stored row
        :raises StoreRejected: if the row is not there afterwards
        """
        store.add_plant_info(self.db_path, record)

        stored = self.read_species(record["plant_id"])
        if not stored:
            raise StoreRejected("plant_info upsert was not stored")

        return stored

    # -- readings (local measured data) -----------------------------------

    def read_latest_reading(self, user_plant_id: int) -> dict:
        """
        :return: The newest reading for this plant, or {} if it has none
        """
        return store.read_user_plant_log(user_plant_id, self.db_path)

    def read_readings(self, user_plant_id: int, limit: int = 100) -> List[dict]:
        """
        :return: Up to `limit` readings for this plant, newest first
        """
        return store.read_user_plant_logs(user_plant_id, self.db_path, limit)

    def _all_readings(self, user_plant_id: int) -> List[dict]:
        # limit=-1 means no limit in SQLite, which is how delete_user_plant_log
        # collects the rows it is about to remove.
        return store.read_user_plant_logs(user_plant_id, self.db_path, -1)

    def add_reading(self, user_plant_id: int, record: dict) -> dict:
        """
        Log one reading and return it as stored.

        Confirmation counts rows rather than re-reading "the latest", because a
        client may supply a `time_stamp` older than rows already logged, and the
        latest-reading query orders by time -- it would not surface the new row.
        The new row is instead the one with the highest log_id, which is
        AUTOINCREMENT and so always the most recently inserted.

        :param user_plant_id: Which of the user's plants the reading came from
        :param record: Reading fields, without user_plant_id
        :return: The stored row
        :raises StoreRejected: if no row was added
        """
        row = dict(record, user_plant_id=user_plant_id)

        before = len(self._all_readings(user_plant_id))
        store.add_user_plant_log(self.db_path, row)
        after = self._all_readings(user_plant_id)

        if len(after) <= before:
            raise StoreRejected("reading was not stored")

        return max(after, key=lambda reading: reading["log_id"])

    def read_readings_near(
        self,
        pos_x: float,
        pos_y: float,
        radius: float = 50.0,
        limit: int = 100,
    ) -> List[dict]:
        """
        :return: Readings taken within `radius` of the point, nearest first
        """
        return store.read_user_logs_near(pos_x, pos_y, radius, self.db_path, limit)

    def delete_readings(self, user_plant_id: int) -> List[dict]:
        """
        Delete every reading for one plant.

        :return: The deleted rows, or [] if there was nothing to delete
        """
        return store.delete_user_plant_log(user_plant_id, self.db_path)


def build_gateway(db_path: Optional[Path] = None) -> StoreGateway:
    """
    Build a gateway, defaulting to the database the API is configured to serve.

    :param db_path: Override, used by tests to point at a temporary file
    """
    if db_path is None:
        from api.config import resolve_db_path

        db_path = resolve_db_path()

    return StoreGateway(db_path)