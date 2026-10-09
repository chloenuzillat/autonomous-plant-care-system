# Unity API

The Unity project in `simulation/unity` cannot call Python, so the plant and
sensor data in `data/environmental_sensors/store.py` is served over HTTP by the
`api/` package. This is how the two halves exchange data.

## What it is, and what it is not

It is **data-only**. It serves the global care ranges for a species, serves and
accepts sensor readings, and nothing else.

It does **not** drive the robot, run a simulation, or own a floor plan. Unity
owns its world: its scene is the authoritative map, and it sends positions along
with each reading. There is deliberately no `/map` endpoint — if Python also
described the floor plan, the two would eventually disagree about it.

## Running the server

```sh
pip install -e ".[api]"
python -m api.main
```

That serves `data/plant_robot.db` on `http://127.0.0.1:8000`. Interactive,
always-current documentation is at `http://127.0.0.1:8000/docs` — treat it as
the reference, since it is generated from the code.

Point it at a different database with `PLANT_DB_PATH` (the same variable
`data/config.py` already honours), which is the way to experiment without
writing into the real one:

```sh
PLANT_DB_PATH=/tmp/scratch.db python -m api.main
```

Other variables: `PLANT_API_HOST`, `PLANT_API_PORT`, `PLANT_API_RELOAD`,
`PLANT_API_CORS_ORIGINS`.

## Endpoints

| Method | Path | What it does |
| --- | --- | --- |
| GET | `/health` | Liveness, and which database file is being served |
| GET | `/species/{plant_id}` | The care ranges every plant of this species wants |
| PUT | `/species/{plant_id}` | Insert or replace those ranges |
| GET | `/plants/{user_plant_id}/readings` | Readings for one plant, newest first (`?limit=`, default 100) |
| GET | `/plants/{user_plant_id}/readings/latest` | The newest reading for one plant |
| POST | `/plants/{user_plant_id}/readings` | Log one reading; returns it as stored |
| DELETE | `/plants/{user_plant_id}/readings` | Delete every reading for one plant; returns what it deleted |
| GET | `/readings/near` | Readings near a point, nearest first (`pos_x`, `pos_y`, `radius`, `limit`) |
| WS | `/ws` | Push channel: readings as they are logged |

### The two ids

Both appear in a reading, because the user can own several plants of the same
species — see `data/README.md`.

- `user_plant_id` — which individual pot. It is the **path** parameter, and
  readings are grouped, queried and deleted by it.
- `plant_id` — what species that pot is, and the key `/species` is keyed by.

## Three things to know before writing a client

**1. Lists arrive wrapped.** Never a bare JSON array:

```json
{ "count": 2, "readings": [ { "log_id": 1, ... }, { "log_id": 2, ... } ] }
```

Unity's built-in `JsonUtility` cannot deserialize a top-level array, so the
envelope keeps it a usable fallback.

**2. `null` is not `0`.** Every reading field is nullable, and `null` means the
measurement was never taken. A plant with no soil sensor is not a plant in bone
dry soil. Send `null` explicitly for a sensor you do not have — the three
ambient fields (`lux_reading`, `temp_reading`, `humidity_reading`) must be
present in the body, so that "no sensor" can never be confused with "forgot to
send it". This is why the C# client uses `double?` and Newtonsoft rather than
`JsonUtility`, which would silently turn a missing reading into `0`.

**3. The y axis points the other way.** Stored positions use origin top-left
with y growing **downward**, inherited from the floor plan the existing readings
were taken in. Unity's y grows **up**. Flip it on the Unity side:

```csharp
PosY = floorHeight - robot.transform.position.z;
```

The client does not flip it for you, because only your scene knows its extents.

## The push channel

`/ws` is the one endpoint that does not wait to be asked. Connect to
`ws://127.0.0.1:8000/ws` and the server sends:

- a **`hello`** frame immediately, naming the database it serves, so a client
  can confirm it reached the right server;
- a **`reading`** frame for every reading logged through
  `POST /plants/{id}/readings`, carrying the row *as stored* — so the client
  learns the `log_id` and the database's timestamp without asking;
- a **`pong`** in reply to `{"type": "ping"}`, which is the only thing a client
  needs to send. Everything else it sends is ignored: writes go over HTTP.

Every frame is the same envelope, so one deserializer handles all of them:

```json
{ "type": "reading", "seq": 7, "sent_at": "2026-10-08 18:42:07",
  "reading": { "log_id": 12, "user_plant_id": 1, "lux_reading": 1846.8, ... } }
```

`seq` increments by one per frame per connection; a gap means frames were
dropped, which happens when a client stops reading. Ignore frame types you do
not recognise rather than treating them as errors, so new ones can be added
without breaking you.

### Drive commands — reserved, not implemented

There is a fourth frame type, `command`, that **nothing sends today**. Its shape
is settled because the Unity client is already written against it:

```json
{ "type": "command", "seq": 9, "sent_at": "...",
  "command": { "throttle": 0.4, "steer": -0.25, "handbrake": false } }
```

`throttle` and `steer` are both in `[-1, 1]`. See `DriveCommand` in
`api/schemas.py`. Deliberately left blank on the Python side for now: deciding
how the robot should move is not this API's job, and there is no controller to
decide it yet.

To turn it on, broadcast from wherever that decision ends up being made — the
hub does not care who publishes:

```python
hub.publish("command", command=command.model_dump())
```

A command is a **state, not an impulse** — it stays in effect until the next one
arrives. Whoever enables this should know the client stops its robot if commands
go quiet, rather than holding the last throttle forever; on the Unity side that
is `SocketCommandDriver`'s staleness timeout.

### What the push does not see

Broadcasts fire from the HTTP handler, so only writes that come **through this
process** are visible. Python code calling `store.add_user_plant_log` directly
bypasses the API and no frame is sent. There is no change notification in SQLite
to fall back on — no triggers, no update hook — so if out-of-process writes ever
become real, this needs a poller watching the high-water `log_id` rather than a
tweak.

## Unity setup

1. The Newtonsoft dependency is already in `Packages/manifest.json`
   (`com.unity.nuget.newtonsoft-json`); Unity restores it on next open.
2. `Assets/Scripts/PlantRobotClient.cs` and `PlantRobotDtos.cs` are in place.
3. Attach `PlantRobotClient` to a GameObject and set **Base Url** in the
   inspector (default `http://127.0.0.1:8000`).
4. Start the server before entering Play mode.

Every method takes an `onSuccess` and an `onError` callback, so a failed save is
something the scene can react to rather than something only the console sees.
The server's own explanation is included in the error message — FastAPI returns
it in a `detail` field.

```csharp
client.PostReading(1, new ReadingCreate {
    PlantId = 1,
    LuxReading = 1840.0,
    TempReading = 22.3,
    HumidityReading = 42.8,
    SoilMoisturePct = null,          // no soil sensor on this pot
    PosX = robot.transform.position.x,
    PosY = floorHeight - robot.transform.position.z,
    HeadingDeg = robot.transform.eulerAngles.y,
}, stored => Debug.Log($"saved as log {stored.LogId}"),
   error => Debug.LogError(error));
```

## Caveats

- **No authentication.** The server binds `127.0.0.1` and anyone who can reach
  it can read and delete every reading. Do not set `PLANT_API_HOST=0.0.0.0`
  outside a network you trust — and bear that in mind before enabling the
  `command` frame, which would let the same anyone drive the robot.
- **WebGL builds need CORS.** They run in a browser and are subject to it; the
  default `PLANT_API_CORS_ORIGINS=*` covers development. Native players are not
  affected. Note CORS middleware does **not** apply to the WebSocket handshake,
  so `/ws` accepts any origin regardless of that setting.
- **WebGL cannot use the C# socket client.** `ClientWebSocket` needs
  `System.Net` sockets, which a browser build does not have. A WebGL target
  means swapping `PlantSocketClient` for a jslib-backed package such as
  NativeWebSocket; nothing else about the contract changes.
- **Android builds block cleartext HTTP** by default. Use HTTPS, or allow
  cleartext for your host, if the robot is ever driven from a phone.
- **One writer at a time** is the comfortable assumption. SQLite serialises
  writes, so a second one arriving mid-transaction can hit a lock. Nothing
  batches writes today, and readings arrive far too slowly for it to matter.

## Where this sits

`api/` is a server, and for the HTTP endpoints it is deliberately *not* in
`pi/communication/unity_client.py` — that file is reserved for Pi-side code that
calls **out** to Unity.

`/ws` bends that rule: a push means `api/` does initiate traffic toward Unity.
It stays here anyway, because the connection is still opened *by* the client and
the server only answers on a socket it was handed. `unity_client.py` remains the
place for code that goes looking for Unity on its own.

- `api/schemas.py` — request and response shapes. Request models forbid unknown
  fields on purpose; see the note at the top of the file.
- `api/hub.py` — the WebSocket fan-out. Publishers are sync handlers on worker
  threads, so they queue rather than send; one task drains the queue. The
  reasoning is at the top of the file.
- `api/store_gateway.py` — the only place that talks to `store.py`. It exists
  because the store's writers report failure by returning `None`, exactly as
  they do on success, so every write here is confirmed by reading back.
- `api/app.py` — the routes.
- `tests/test_api.py` — run with `pytest tests/ -v`.
