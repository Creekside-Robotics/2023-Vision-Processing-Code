from ..constants import GameField
from ..utils import Pose, Translation


class Robot:
    """Represents the robot on the game field"""

    size = GameField.robot_radius
    color = "Red"
    mode = "Manual"

    def __init__(
        self,
        pose: Pose = Pose(Translation(0, 0), 0),
        velocity: tuple[float, float] = (0, 0),
        angular_velocity: float = 0,
    ):
        self.pose = pose
        self.velocity = velocity
        self.angular_velocity = angular_velocity
