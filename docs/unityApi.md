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
  outside a network you trust.
- **WebGL builds need CORS.** They run in a browser and are subject to it; the
  default `PLANT_API_CORS_ORIGINS=*` covers development. Native players are not
  affected.
- **Android builds block cleartext HTTP** by default. Use HTTPS, or allow
  cleartext for your host, if the robot is ever driven from a phone.
- **One writer at a time** is the comfortable assumption. SQLite serialises
  writes, so a second one arriving mid-transaction can hit a lock. Nothing
  batches writes today, and readings arrive far too slowly for it to matter.

## Where this sits

`api/` is a server, so it is deliberately *not* in
`pi/communication/unity_client.py` — that file is reserved for Pi-side code that
calls **out** to Unity, the opposite direction.

- `api/schemas.py` — request and response shapes. Request models forbid unknown
  fields on purpose; see the note at the top of the file.
- `api/store_gateway.py` — the only place that talks to `store.py`. It exists
  because the store's writers report failure by returning `None`, exactly as
  they do on success, so every write here is confirmed by reading back.
- `api/app.py` — the routes.
- `tests/test_api.py` — run with `pytest tests/ -v`.
