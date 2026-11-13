
import requests


class UnityClient:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")

    def send_wheel_command(self, left_speed, right_speed):
        response = requests.post(
            f"{self.base_url}/robot/command",
            json={
                "left_speed": left_speed,
                "right_speed": right_speed
            },
            timeout=2
        )

        response.raise_for_status()
        return response.json()

    def get_pose(self):
        response = requests.get(
            f"{self.base_url}/robot/pose",
            timeout=2
        )

        response.raise_for_status()
        return response.json()