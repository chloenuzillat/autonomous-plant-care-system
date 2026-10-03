"""The FastAPI application.

Run it with ``python -m api.main``, or ``uvicorn api.app:app --reload``.

Every handler is a plain ``def``, so FastAPI runs it in a worker thread. That is
safe here because the store opens a fresh sqlite3 connection inside each call
and closes it before returning, so no connection is ever shared across threads.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Path as PathParam, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api import config
from api.schemas import (
    Health,
    Reading,
    ReadingCreate,
    ReadingList,
    SpeciesInfo,
    SpeciesUpsert,
)
from api.store_gateway import StoreRejected, build_gateway

DESCRIPTION = """
Read/write access to the plant care system's data for clients outside Python --
a Unity project in particular.

This API is **data-only**. It serves species care ranges and logged sensor
readings, and accepts readings back. It does not control the robot and does not
run a simulation: the client owns its own world.

Three things to know before writing a client:

* Lists come wrapped in an object (`{"count": ..., "readings": [...]}`), never
  as a bare JSON array, because Unity's `JsonUtility` cannot parse a top-level
  array.
* Every reading field is nullable. `null` means the measurement was never taken,
  which is not the same as `0`.
* Positions are whatever floor plan the client is measuring in. The readings
  already stored use origin top-left with y growing **downward**, which is the
  opposite of Unity's convention, so a client must flip it. There is no `/map`
  endpoint: the Unity scene is the authoritative floor plan, not Python.
"""


def _reading_list(rows: List[dict]) -> ReadingList:
    """Wrap rows in the list envelope."""
    return ReadingList(count=len(rows), readings=[Reading(**row) for row in rows])


def create_app(db_path: Optional[Path] = None) -> FastAPI:
    """
    Build the application.

    :param db_path: Database to serve. Defaults to the configured one; tests
        pass a temporary file.
    """
    gateway = build_gateway(db_path)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Idempotent, and it also runs the store's column migrations, so an
        # older database file is brought up to date before the first request.
        gateway.init()
        yield

    app = FastAPI(
        title="Autonomous Plant Care System API",
        description=DESCRIPTION,
        version="0.1.0",
        lifespan=lifespan,
    )

    app.state.gateway = gateway

    # Only Unity WebGL builds are subject to CORS; native players are not.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(StoreRejected)
    async def _store_rejected(request: Request, exc: StoreRejected) -> JSONResponse:
        # The request was valid as far as this API could tell, and the store
        # still refused it. That is a bug here, not in the client's request.
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"The store did not accept the write: {exc}"},
        )

    @app.get("/health", response_model=Health, tags=["meta"])
    def health() -> Health:
        """Report liveness and which database file is being served."""
        return Health(status="ok", db_path=str(gateway.db_path))

    @app.get("/species/{plant_id}", response_model=SpeciesInfo, tags=["species"])
    def read_species(plant_id: int = PathParam(..., ge=1)) -> SpeciesInfo:
        """The care ranges every plant of this species wants."""
        row = gateway.read_species(plant_id)
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No species with plant_id {plant_id}",
            )

        return SpeciesInfo(**row)

    @app.put("/species/{plant_id}", response_model=SpeciesInfo, tags=["species"])
    def upsert_species(
        species: SpeciesUpsert,
        plant_id: int = PathParam(..., ge=1),
    ) -> SpeciesInfo:
        """
        Insert or replace one species' care ranges.

        The id in the path wins as the resource's identity, so a body
        disagreeing with it is a conflict rather than a silent write to the
        wrong row.
        """
        if species.plant_id != plant_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"plant_id in body ({species.plant_id}) does not match "
                    f"the path ({plant_id})"
                ),
            )

        return SpeciesInfo(**gateway.upsert_species(species.model_dump()))

    @app.get(
        "/plants/{user_plant_id}/readings",
        response_model=ReadingList,
        tags=["readings"],
    )
    def read_readings(
        user_plant_id: int = PathParam(..., ge=1),
        limit: int = Query(100, ge=1, le=1000),
    ) -> ReadingList:
        """Readings logged for one of the user's plants, newest first."""
        return _reading_list(gateway.read_readings(user_plant_id, limit))

    @app.get(
        "/plants/{user_plant_id}/readings/latest",
        response_model=Reading,
        tags=["readings"],
    )
    def read_latest_reading(user_plant_id: int = PathParam(..., ge=1)) -> Reading:
        """The most recent reading logged for one of the user's plants."""
        row = gateway.read_latest_reading(user_plant_id)
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No readings logged for user_plant_id {user_plant_id}",
            )

        return Reading(**row)

    @app.post(
        "/plants/{user_plant_id}/readings",
        response_model=Reading,
        status_code=status.HTTP_201_CREATED,
        tags=["readings"],
    )
    def add_reading(
        reading: ReadingCreate,
        user_plant_id: int = PathParam(..., ge=1),
    ) -> Reading:
        """
        Log one sensor reading for one of the user's plants.

        Returns the row as stored, including the `log_id` and the `time_stamp`
        the database stamped on it.
        """
        row = gateway.add_reading(user_plant_id, reading.model_dump())

        return Reading(**row)

    @app.delete(
        "/plants/{user_plant_id}/readings",
        response_model=ReadingList,
        tags=["readings"],
    )
    def delete_readings(user_plant_id: int = PathParam(..., ge=1)) -> ReadingList:
        """
        Delete every reading logged for one of the user's plants.

        Returns what was deleted, so a client that did not mean it still has the
        data. Deleting a plant with no readings is not an error.
        """
        return _reading_list(gateway.delete_readings(user_plant_id))

    @app.get("/readings/near", response_model=ReadingList, tags=["readings"])
    def read_readings_near(
        pos_x: float = Query(..., description="x on the client's floor plan"),
        pos_y: float = Query(..., description="y on the client's floor plan"),
        radius: float = Query(50.0, gt=0),
        limit: int = Query(100, ge=1, le=1000),
    ) -> ReadingList:
        """
        Readings taken anywhere near a point, nearest first.

        Spans every plant, not one: this answers "what are conditions like over
        there", which is about the spot rather than about any one pot.
        """
        rows = gateway.read_readings_near(pos_x, pos_y, radius, limit)

        return _reading_list(rows)

    return app


app = create_app()
