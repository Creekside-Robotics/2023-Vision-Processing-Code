import math

from .utils import Pose, Translation


class GameField:
    # Game field class storing game field relative data
    field_boundary = (0, 0, 10, 7)
    dead_zones = [(4.5, 3, 5.5, 4)]

    reference_points = {
        1: Pose(Translation(4.5, 3.5), 0),
        2: Pose(Translation(x=5, y=3), math.pi / 2),
        3: Pose(Translation(5.5, 3.5), math.pi),
        4: Pose(Translation(5, 4), 3 * math.pi / 2),
    }

    apriltag_size = 0.1524
    apriltag_family = "tag16h5"

    robot_radius = 0.5
