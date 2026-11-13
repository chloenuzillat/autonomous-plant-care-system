
from pi.robot.robot import Robot
from pi.communication.unity_client import UnityClient


class UnityRobot(Robot):
    def __init__(self, client: UnityClient):
        self.client = client

    def move(self, left_speed, right_speed):
        self.client.send_wheel_command(left_speed, right_speed)

    def stop(self):
        self.move(0, 0)

    def get_position(self):
        pose = self.client.get_pose()
        return pose["x"], pose["y"]

    def get_orientation(self):
        pose = self.client.get_pose()
        return pose["heading_deg"]

    def get_encoder_data(self):
        raise NotImplementedError(
            "Encoder data is not available in the Unity simulation."
        )