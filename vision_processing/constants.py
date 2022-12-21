import math

from . import Camera, DynamicObject
from .utils import Box, Pose, Translation


class GameField:
    # Game field class storing game field relative data
    field_boundary = Box(Translation(0, 0), Translation(10, 7))
    dead_zones = [Box(Translation(4.5, 3), Translation(5.5, 4))]

    reference_points = {
        1: Pose(Translation(4.5, 3.5), 0),
        2: Pose(Translation(x=5, y=3), math.pi / 2),
        3: Pose(Translation(5.5, 3.5), math.pi),
        4: Pose(Translation(5, 4), 3 * math.pi / 2),
    }

    apriltag_size = 0.1524
    apriltag_family = "tag16h5"

    prediction_decay = 0.7
    robot_radius = 0.5
    robot_translational_speed = 1
    robot_angular_speed = math.pi

    home_location = DynamicObject(
        Translation(1.5, 5.5),
        1.5,
        "Home Square",
        0,
        absolute_coordinates=Translation(1.5, 5.5),
    )
    home_location.id = 0

    endgame_square = DynamicObject(
        Translation(1, 1),
        0,
        "Endgame Square",
        0,
        absolute_coordinates=Translation(0, 0),
    )
    endgame_square.id = 1

    scout_position_one = DynamicObject(
        Translation(5, 0.5), 0, "Scout", 0, absolute_coordinates=Translation(5, 0.5)
    )
    scout_position_one.id = 2

    special_objects = [home_location, endgame_square, scout_position_one]

    special_task_rotations = {
        "Endgame Square": 0,
        "Scout": math.pi / 4,
        "Home Square": 0,
    }

    special_boundaries = {
        Box(
            Translation(0, 4),
            Translation(3, 7)
        ),
        Box(
            Translation(0.5, 0.5),
            Translation(1.5, 1.5)
        )
    }

    cameras = [
        Camera((0.106, 0, 0.6606), (-math.pi / 6, 0), 636, 0),
        Camera((-0.106, 0, 0.6606), (-math.pi / 6, math.pi), 734, 1),
    ]
