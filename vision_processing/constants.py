import math

from .utils import Box, Pose, Translation


class GameField:
    # Game field class storing game field relative data
    field_boundary = Box(Translation(0, 0), Translation(10, 7))
    dead_zones = [Box(Translation(4.75, 3.25), Translation(5.25, 3.75))]

    reference_points = {
        0: Pose(Translation(4.75, 3.5), 0),
        1: Pose(Translation(x=5, y=3), math.pi / 2),
        2: Pose(Translation(5.5, 3.5), math.pi),
        3: Pose(Translation(5, 4), 3 * math.pi / 2),
    }

    apriltag_size = 0.1224
    apriltag_family = "tag16h5"

    prediction_decay = 0.6
    robot_radius = 0.5
    robot_translational_speed = 1
    robot_angular_speed = math.pi

    home_location = (
        Translation(1.5, 5.5),
        1.5,
        "Home Square",
        0,
        Translation(1.5, 5.5),
        0
    )

    endgame_square = (
        Translation(1, 1),
        0,
        "Endgame Square",
        0,
        Translation(0, 0),
        1
    )

    scout_position_one = (
        Translation(5, 0.5), 0, "Scout", 0, Translation(5, 0.5), 2
    )

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
        ((0.106, 0, 0.6606), (-math.pi / 6, 0), 636, 0),
        ((-0.106, 0, 0.6606), (-math.pi / 6, math.pi), 734, 1),
    ]
