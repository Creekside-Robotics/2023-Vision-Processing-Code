import math

from .utils import Box, Pose, Translation


class GameField:
    # Game field class storing game field relative data
    field_boundary = Box(Translation(0, 0), Translation(5.9436, 3.6576))
    dead_zones = [Box(Translation(6*0.4572, 3*0.4572), Translation(8*0.4572, 5*0.4572))]

    reference_points = {
        0: Pose(Translation(6*0.4572, 4*0.4572), 0)
    }

    apriltag_size = 0.1224
    apriltag_family = "tag16h5"

    prediction_decay = 0.6
    robot_radius = 0.5
    robot_translational_speed = 1
    robot_angular_speed = math.pi

    home_location = (
        Translation(1.5 * 0.4572, 6.5 * 0.4572),
        1.5,
        "Home Square",
        0,
        Translation(1.5 * 0.4572, 6.5 * 0.4572),
        0
    )

    endgame_square = (
        Translation(2 * 0.4572, 2 * 0.4572),
        0,
        "Endgame Square",
        0,
        Translation(2 * 0.4572, 2 * 0.4572),
        1
    )

    scout_position_one = (
        Translation(7 * 0.4572, 2 * 0.4572), 0, "Scout", 0, Translation(7 * 0.4572, 2 * 0.4572), 2
    )

    special_objects = [home_location, endgame_square, scout_position_one]

    special_task_rotations = {
        "Endgame Square": 0,
        "Scout": math.pi / 4,
        "Home Square": 0,
    }

    special_boundaries = {
        Box(
            Translation(0 * 0.4572, 5 * 0.4572),
            Translation(3 * 0.4572, 8 * 0.4572)
        ),
        Box(
            Translation(0 * 0.4572, 5 * 0.4572),
            Translation(3 * 0.4572, 8 * 0.4572)
        )
    }

    cameras = [
        ((0.106, 0, 0.6606), (-math.pi / 6, 0), 636, 0),
        # ((-0.106, 0, 0.6606), (-math.pi / 6, math.pi), 734, 0),
    ]
