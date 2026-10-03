"""Request and response shapes for the API.

Two rules run through this module:

* **Request models forbid unknown fields.** The store's writers reject a record
  carrying a key they do not know by returning silently
  (``add_user_plant_log`` in data/environmental_sensors/store.py), which an HTTP
  layer cannot turn into a status code. Forbidding extras here means a typo
  comes back as a 422 naming the field instead of a write that quietly did
  nothing.
* **Response models do not.** They are built from database rows, so a column
  added to the table later should widen the response, not fail every read.

List responses are wrapped in an envelope rather than returned as a bare JSON
array, because Unity's built-in ``JsonUtility`` cannot deserialize a top-level
array.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class _Strict(BaseModel):
    """Base for request bodies: unknown fields are an error, not a surprise."""

    model_config = ConfigDict(extra="forbid")


class SpeciesUpsert(_Strict):
    """
    The global care ranges for one species, as supplied by a client.

    No ``last_updated``: the store stamps that itself, and rejects any record
    that carries it.
    """

    plant_id: int = Field(..., ge=1, description="plant_info.plant_id")
    plant_name: str = Field(..., min_length=1)
    lux_min: Optional[float] = None
    lux_max: Optional[float] = None
    temp_min_celsius: Optional[float] = None
    temp_max_celsius: Optional[float] = None
    humidity_min_pct: Optional[float] = None
    humidity_max_pct: Optional[float] = None
    source: Optional[str] = Field(
        None, description="Where the ranges came from, e.g. 'perenual' or 'manual'"
    )


class SpeciesInfo(BaseModel):
    """One plant_info row: what every plant of this species wants."""

    plant_id: int
    plant_name: str
    lux_min: Optional[float] = None
    lux_max: Optional[float] = None
    temp_min_celsius: Optional[float] = None
    temp_max_celsius: Optional[float] = None
    humidity_min_pct: Optional[float] = None
    humidity_max_pct: Optional[float] = None
    source: Optional[str] = None
    last_updated: Optional[str] = None


class ReadingCreate(_Strict):
    """
    One sensor reading, as posted by a client. ``user_plant_id`` comes from the
    path, so it is not a field here.

    The three ambient readings are required but nullable, which mirrors the
    store exactly: it insists the keys are present, and the columns themselves
    accept NULL for a measurement that was never taken. Send ``null`` for a
    sensor you do not have rather than omitting the field, so "no sensor" is
    never mistaken for "forgot to send it".
    """

    plant_id: int = Field(..., ge=1, description="Species id of this pot")
    lux_reading: Optional[float] = Field(..., description="Ambient light, lux")
    temp_reading: Optional[float] = Field(..., description="Ambient temperature, Celsius")
    humidity_reading: Optional[float] = Field(..., description="Relative humidity, percent")
    soil_moisture_pct: Optional[float] = Field(
        None, ge=0, le=100, description="Moisture inside this pot, percent"
    )
    pos_x: Optional[float] = Field(None, description="Robot x when it took the reading")
    pos_y: Optional[float] = Field(None, description="Robot y when it took the reading")
    heading_deg: Optional[float] = Field(
        None, description="Robot heading, degrees; 0 faces +x, 90 faces up"
    )
    time_stamp: Optional[str] = Field(
        None, description="'YYYY-MM-DD HH:MM:SS'; defaults to now if omitted"
    )

    @field_validator("heading_deg")
    @classmethod
    def _wrap_heading(cls, value: Optional[float]) -> Optional[float]:
        # The column has a CHECK keeping this in [0, 360), and the store wraps
        # it on the way in. Wrapping here too means the value echoed back in the
        # response is the value that was stored.
        return None if value is None else float(value) % 360


class Reading(BaseModel):
    """One user_plant_log row as stored."""

    log_id: int
    user_plant_id: int
    plant_id: int
    lux_reading: Optional[float] = None
    temp_reading: Optional[float] = None
    humidity_reading: Optional[float] = None
    soil_moisture_pct: Optional[float] = None
    pos_x: Optional[float] = None
    pos_y: Optional[float] = None
    heading_deg: Optional[float] = None
    time_stamp: Optional[str] = None
    # Only the near-position query computes this; it is absent everywhere else.
    distance_squared: Optional[float] = None


class ReadingList(BaseModel):
    """Envelope for any list of readings."""

    count: int
    readings: List[Reading]


class Health(BaseModel):
    """Liveness, plus which database file is actually being served."""

    status: str
    db_path: str
