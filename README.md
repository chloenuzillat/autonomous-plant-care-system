# autonomous-plant-care-system

A small wheeled robot that uses a camera and environmental sensors (light, temperature, humidity) to map a space and determine the best location for a specific plant. An AI system learns placement suitability over time by observing the plant's actual response, and can physically relocate the plant to improve conditions, continuously refining its decisions through feedback. Future extensions include soil-based watering prediction for vacation care and a virtual plant avatar to reflect soil health.

## Run API

The Unity project talks to the Python side over HTTP. Start the server with:

```sh
pip install -e ".[api]"
python -m api.main
```

It serves plant species ranges and sensor readings on `http://127.0.0.1:8000`,
with interactive docs at `http://127.0.0.1:8000/docs`.

See `docs/unityApi.md` for the endpoints and for the Unity side.

## Run Tests

```sh
pip install -e ".[api,dev]"
pytest tests/ -v
```

## Look at `docs/technicalPlan.md` for more details on the project
