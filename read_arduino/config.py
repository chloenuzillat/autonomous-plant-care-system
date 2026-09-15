"""Central paths and settings. Import this instead of hardcoding paths."""

import os
from pathlib import Path

# config.py lives in read_arduino/, so the repo root is one level up.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Everything the pipeline writes goes here.
DATA_DIR = Path(os.environ.get("PLANT_DATA_DIR", PROJECT_ROOT / "data"))

# Override on the Pi with:  export PLANT_DB_PATH=/home/pi/plant_robot.db
DB_PATH = Path(os.environ.get("PLANT_DB_PATH", DATA_DIR / "plant_robot.db"))

DATA_DIR.mkdir(parents=True, exist_ok=True)