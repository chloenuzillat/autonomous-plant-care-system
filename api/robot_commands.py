
from fastapi import APIRouter, Request

from api.schemas import WheelCommand

from pydantic import BaseModel

class RobotPose(BaseModel):
    x: float
    y: float
    heading_deg: float

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


@router.post("/pose")
def set_pose(pose: RobotPose, request: Request):
    request.app.state.robot_pose = pose.model_dump()
    return {"status": "ok"}


@router.get("/pose")
def get_pose(request: Request):
    return getattr(request.app.state, "robot_pose", None)