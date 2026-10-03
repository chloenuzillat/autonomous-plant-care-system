"""Entry point for the API server.

    python -m api.main

Serve a scratch database instead of the real one with:

    PLANT_DB_PATH=/tmp/scratch.db python -m api.main
"""

import uvicorn

from api.config import HOST, PORT, RELOAD, resolve_db_path


def main() -> None:
    """Start the server on the configured host and port."""
    print(f"Serving {resolve_db_path()}")
    print(f"API docs: http://{HOST}:{PORT}/docs")

    # Passed as an import string rather than the app object, because uvicorn
    # needs to be able to re-import the module when reload is on.
    uvicorn.run("api.app:app", host=HOST, port=PORT, reload=RELOAD)


if __name__ == "__main__":
    main()
