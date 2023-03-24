import math

from .utils import Box, Pose, Translation


class GameField:
    # Game field class storing game field relative data
    field_boundary = Box(Translation(0, 0), Translation(5.9436, 3.6576))
    dead_zones = [Box(Translation(6*0.4572, 3*0.4572), Translation(8*0.4572, 5*0.4572))]

    reference_points = {
        1: Pose(Translation(15.513558, 1.071626), 0),
        2: Pose(Translation(15.513558, 2.748026), 0),
        3: Pose(Translation(15.513558, 4.424426), 0),
        4: Pose(Translation(16.178784, 6.749796), 0),
        5: Pose(Translation(0.36195, 6.749796), math.pi),
        6: Pose(Translation(1.02743, 4.424426), math.pi),
        7: Pose(Translation(1.02743, 2.748026), math.pi),
        8: Pose(Translation(1.02743, 1.071626), math.pi)
    }

    apriltag_size = 0.1524
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
        ((0.1143, -0.3766, 0.8001), (0, -0.4887), 330, 1)
    ]

    test_camera = (
            (0.106, 0, 0.6606),
            (0, -math.pi / 7.5),
            650,
            "testing/testing_resources/HyperClock Test Video.mp4"
    )
