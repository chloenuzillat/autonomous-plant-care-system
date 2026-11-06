"""Tests for the HTTP API in api/.

Each test gets its own database under tmp_path, so nothing here touches the
real one in data/.
"""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from api.app import create_app
from api.schemas import DriveCommand, ReadingCreate, SocketEnvelope
from data.environmental_sensors import store

SNAKE_PLANT = {
    "plant_id": 1,
    "plant_name": "Snake Plant",
    "lux_min": 500.0,
    "lux_max": 10000.0,
    "temp_min_celsius": 15.0,
    "temp_max_celsius": 29.0,
    "humidity_min_pct": 30.0,
    "humidity_max_pct": 50.0,
    "source": "perenual",
}

# A reading with every ambient sensor reporting. Copied and edited by the tests
# that need a variation.
READING = {
    "plant_id": 1,
    "lux_reading": 1846.8,
    "temp_reading": 22.3,
    "humidity_reading": 42.8,
    "soil_moisture_pct": 27.8,
    "pos_x": 126.5,
    "pos_y": 123.0,
    "heading_deg": 137.2,
}


@pytest.fixture
def client(tmp_path):
    """A client against an empty database of its own."""
    with TestClient(create_app(tmp_path / "test.db")) as test_client:
        yield test_client


def test_health_reports_the_database_it_serves(client, tmp_path):
    body = client.get("/health").json()

    assert body["status"] == "ok"
    assert body["db_path"] == str(tmp_path / "test.db")


def test_species_round_trip(client):
    assert client.put("/species/1", json=SNAKE_PLANT).status_code == 200

    stored = client.get("/species/1").json()

    assert stored["plant_name"] == "Snake Plant"
    assert stored["lux_min"] == 500.0
    # Stamped by the store, not by the client.
    assert stored["last_updated"]


def test_species_upsert_replaces_the_existing_row(client):
    client.put("/species/1", json=SNAKE_PLANT)
    client.put("/species/1", json=dict(SNAKE_PLANT, lux_min=750.0))

    assert client.get("/species/1").json()["lux_min"] == 750.0


def test_species_id_in_body_must_match_the_path(client):
    response = client.put("/species/2", json=SNAKE_PLANT)

    assert response.status_code == 409
    # The mismatched write must not have happened under either id.
    assert client.get("/species/1").status_code == 404
    assert client.get("/species/2").status_code == 404


def test_unknown_species_is_404(client):
    assert client.get("/species/999").status_code == 404


def test_posting_a_reading_returns_it_as_stored(client):
    response = client.post("/plants/1/readings", json=READING)

    assert response.status_code == 201

    stored = response.json()
    assert stored["log_id"] == 1
    assert stored["user_plant_id"] == 1
    assert stored["lux_reading"] == 1846.8
    # Stamped by the database when the client does not supply one.
    assert stored["time_stamp"]

    assert client.get("/plants/1/readings/latest").json() == stored
    assert client.get("/plants/1/readings").json()["count"] == 1


def test_heading_is_wrapped_into_one_turn(client):
    # The column has a CHECK keeping this below 360, so a client that keeps
    # accumulating rotation must not be rejected.
    stored = client.post("/plants/1/readings", json=dict(READING, heading_deg=450.0)).json()

    assert stored["heading_deg"] == pytest.approx(90.0)


def test_absent_sensors_stay_absent(client):
    # null means the measurement was never taken, and must not come back as 0.
    reading = dict(READING, lux_reading=None, soil_moisture_pct=None)

    stored = client.post("/plants/1/readings", json=reading).json()

    assert stored["lux_reading"] is None
    assert stored["soil_moisture_pct"] is None


def test_backdated_reading_is_still_confirmed(client):
    # The store's latest-reading query orders by time, so a row stamped in the
    # past is not the newest. The API must still recognise it as created.
    client.post("/plants/1/readings", json=READING)

    response = client.post(
        "/plants/1/readings",
        json=dict(READING, time_stamp="2020-01-01 00:00:00"),
    )

    assert response.status_code == 201
    assert response.json()["log_id"] == 2
    assert client.get("/plants/1/readings").json()["count"] == 2


def test_out_of_range_soil_moisture_is_rejected_loudly(client):
    # The store drops such a record silently; the API must not.
    response = client.post("/plants/1/readings", json=dict(READING, soil_moisture_pct=150.0))

    assert response.status_code == 422
    assert client.get("/plants/1/readings").json()["count"] == 0


def test_unknown_field_is_rejected(client):
    response = client.post("/plants/1/readings", json=dict(READING, lux_readng=5.0))

    assert response.status_code == 422


def test_ambient_readings_must_be_stated(client):
    incomplete = {key: value for key, value in READING.items() if key != "temp_reading"}

    assert client.post("/plants/1/readings", json=incomplete).status_code == 422


def test_plant_with_no_readings_is_404(client):
    assert client.get("/plants/42/readings/latest").status_code == 404
    assert client.get("/plants/42/readings").json() == {"count": 0, "readings": []}


def test_readings_are_newest_first_and_limited(client):
    for hour in range(3):
        client.post(
            "/plants/1/readings",
            json=dict(READING, time_stamp=f"2026-09-14 0{hour}:00:00"),
        )

    body = client.get("/plants/1/readings", params={"limit": 2}).json()

    assert body["count"] == 2
    assert [reading["time_stamp"] for reading in body["readings"]] == [
        "2026-09-14 02:00:00",
        "2026-09-14 01:00:00",
    ]


def test_readings_of_other_plants_are_not_mixed_in(client):
    client.post("/plants/1/readings", json=READING)
    client.post("/plants/2/readings", json=READING)

    assert client.get("/plants/1/readings").json()["count"] == 1
    assert client.get("/plants/1/readings").json()["readings"][0]["user_plant_id"] == 1


def test_near_finds_readings_by_distance_not_by_plant(client):
    client.post("/plants/1/readings", json=dict(READING, pos_x=130.0, pos_y=130.0))
    client.post("/plants/2/readings", json=dict(READING, pos_x=690.0, pos_y=490.0))

    nearby = client.get("/readings/near", params={"pos_x": 126.0, "pos_y": 123.0, "radius": 50}).json()

    assert nearby["count"] == 1
    assert nearby["readings"][0]["user_plant_id"] == 1
    assert nearby["readings"][0]["distance_squared"] is not None

    far = client.get("/readings/near", params={"pos_x": 400.0, "pos_y": 300.0, "radius": 20}).json()
    assert far["count"] == 0


def test_delete_returns_what_it_removed(client):
    client.post("/plants/1/readings", json=READING)
    client.post("/plants/1/readings", json=READING)

    deleted = client.delete("/plants/1/readings").json()

    assert deleted["count"] == 2
    assert client.get("/plants/1/readings").json()["count"] == 0
    # Deleting a plant with nothing logged is not an error.
    assert client.delete("/plants/1/readings").json()["count"] == 0


def test_socket_introduces_itself_on_connect(client, tmp_path):
    """
    The first frame names the database, so a client can tell it reached the
    server it meant to before it starts trusting anything else.
    """
    with client.websocket_connect("/ws") as socket:
        hello = socket.receive_json()

    assert hello["type"] == "hello"
    assert hello["db_path"] == str(tmp_path / "test.db")
    assert hello["seq"] == 1


def test_posted_reading_is_pushed_to_the_socket(client):
    with client.websocket_connect("/ws") as socket:
        socket.receive_json()  # hello

        posted = client.post("/plants/1/readings", json=READING).json()
        frame = socket.receive_json()

    assert frame["type"] == "reading"
    # The row as stored, not the body as sent: the client learns the log_id and
    # the timestamp the database stamped without having to ask for them.
    assert frame["reading"]["log_id"] == posted["log_id"]
    assert frame["reading"]["time_stamp"] == posted["time_stamp"]
    assert frame["reading"]["user_plant_id"] == 1


def test_every_client_gets_every_frame(client):
    """Broadcast, not round-robin: two listeners both see the one reading."""
    with client.websocket_connect("/ws") as first, client.websocket_connect("/ws") as second:
        first.receive_json()
        second.receive_json()

        client.post("/plants/1/readings", json=READING)

        assert first.receive_json()["type"] == "reading"
        assert second.receive_json()["type"] == "reading"


def test_sequence_numbers_increase_so_gaps_are_visible(client):
    with client.websocket_connect("/ws") as socket:
        socket.receive_json()  # hello is seq 1

        client.post("/plants/1/readings", json=READING)
        client.post("/plants/1/readings", json=READING)

        seqs = [socket.receive_json()["seq"], socket.receive_json()["seq"]]

    assert seqs == [2, 3]


def test_ping_is_answered(client):
    """
    So a client can prove the connection is alive during a long quiet spell
    instead of waiting for a reading that may be minutes away.
    """
    with client.websocket_connect("/ws") as socket:
        socket.receive_json()  # hello
        socket.send_json({"type": "ping"})

        assert socket.receive_json()["type"] == "pong"


def test_writes_succeed_with_nothing_listening(client):
    """
    The push is a side effect, never a precondition. A reading posted with no
    socket open must store and return exactly as it always did.
    """
    response = client.post("/plants/1/readings", json=READING)

    assert response.status_code == 201
    assert response.json()["log_id"] == 1


def test_socket_frames_match_the_published_envelope(client):
    """
    SocketEnvelope documents the frame shape for clients, but the hub builds
    frames as plain dicts, so nothing stops the two drifting apart. Validate
    one of each kind actually sent against it.
    """
    with client.websocket_connect("/ws") as socket:
        hello = socket.receive_json()
        socket.send_json({"type": "ping"})
        pong = socket.receive_json()
        client.post("/plants/1/readings", json=READING)
        reading = socket.receive_json()

    for frame in (hello, pong, reading):
        SocketEnvelope.model_validate(frame)


def test_drive_command_shape_is_settled_even_though_nothing_sends_one(client):
    """
    DriveCommand is reserved for a controller that does not exist yet, but the
    Unity client is written against it, so its field names and the -1..1 bounds
    are a contract already. Nothing should send one today.
    """
    assert set(DriveCommand.model_fields) == {"throttle", "steer", "handbrake"}

    with pytest.raises(ValidationError):
        DriveCommand(throttle=2.0, steer=0.0)

    # No route accepts or produces one.
    assert client.post("/commands", json={"throttle": 0.0, "steer": 0.0}).status_code == 404


def test_reading_fields_match_the_store():
    """
    Guard against the request model drifting from the store's key sets.

    The store rejects a record carrying a key it does not know, and does so
    silently, so the two definitions have to stay in step. user_plant_id is
    excluded because it comes from the URL path, not the body.
    """
    expected = (
        store.REQUIRED_USER_PLANT_LOG_KEYS | store.OPTIONAL_USER_PLANT_LOG_KEYS
    ) - {"user_plant_id"}

    assert set(ReadingCreate.model_fields) == expected
