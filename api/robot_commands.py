
from fastapi import APIRouter, Request

from api.schemas import WheelCommand

router = APIRouter(prefix="/robot", tags=["robot"])


@router.post("/command")
def set_command(command: WheelCommand, request: Request) -> dict:
    """Broadcast wheel speeds to connected WebSocket clients."""

    request.app.state.hub.publish(
        "command",
        command=command.model_dump()
    )

    return {
        "status": "queued",
        "command": command.model_dump()
    }