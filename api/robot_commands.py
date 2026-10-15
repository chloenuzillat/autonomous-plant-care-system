from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/robot", tags=["robot"])

class WheelCommand(BaseModel):
    left_speed: float = Field(ge=-100, le=100)
    right_speed: float = Field(ge=-100, le=100)

@router.post("/command")
def set_command(command: WheelCommand, request: Request) -> dict:
    """Set the robot's desired left and right wheel speeds."""
    with request.app.state.robot_command_lock:
        current = request.app.state.robot_command
        current["left_speed"] = command.left_speed
        current["right_speed"] = command.right_speed
        current["command_id"] += 1
        return current.copy()

@router.get("/command")
def get_command(request: Request) -> dict:
    """Return the latest desired wheel speeds for Unity."""
    with request.app.state.robot_command_lock:
        return request.app.state.robot_command.copy()