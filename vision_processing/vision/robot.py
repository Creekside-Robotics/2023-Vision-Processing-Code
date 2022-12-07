from ..constants import GameField
from ..utils import Pose


class Robot:
    """Represents the robot on the game field"""

    size = GameField.robot_radius

    def __init__(
        self,
        pose: Pose,
        velocity: tuple[float, float],
        angular_velocity: float,
    ):
        self.pose = pose
        self.velocity = velocity
        self.angular_velocity = angular_velocity
