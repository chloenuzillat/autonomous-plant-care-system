"""Where the API listens and which database it serves.

Follows the same shape as data/config.py: a default that works out of the box,
overridable by an environment variable.
"""

import os
from pathlib import Path

from data.config import DB_PATH as REAL_DB_PATH

# Values an environment variable can carry to mean "yes". Anything else, the
# empty string included, means no.
_TRUTHY = {"1", "true", "yes", "on"}


def _is_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in _TRUTHY


def resolve_db_path() -> Path:
    """
    Pick the database file to serve.

    Read through a function rather than frozen at import, so a test or a script
    can point the app at another file by setting the environment first.

    data.config already honours PLANT_DB_PATH, so there is no second override
    mechanism to learn: set that to serve a scratch database instead of the
    real one.

    :return: Path to the database the API should open
    """
    return Path(os.environ.get("PLANT_DB_PATH", REAL_DB_PATH))


DB_PATH = resolve_db_path()

HOST = os.environ.get("PLANT_API_HOST", "127.0.0.1")
PORT = int(os.environ.get("PLANT_API_PORT", "8000"))
RELOAD = _is_truthy("PLANT_API_RELOAD")

# Only Unity WebGL builds need this: they run in a browser and are subject to
# CORS. Native players are not. Permissive because the API binds loopback and
# holds no secrets -- see the warning in docs/unityApi.md before exposing it.
CORS_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("PLANT_API_CORS_ORIGINS", "*").split(",")
    if origin.strip()
]
