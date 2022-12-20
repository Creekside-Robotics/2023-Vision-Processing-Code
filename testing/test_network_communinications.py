import time

from vision_processing import NetworkCommunication, ReferencePoint, Pose


class TestNetworkCommunication(NetworkCommunication):
    def __init__(self):
        super().__init__()
        self.pose = None
        self.end_time = time.time() + 150

    def set_apriltag_pose_data(self, apriltag_array: list[ReferencePoint]) -> None:
        average_pose = Pose.average_poses([tag.estimatatedRobotPose() for tag in apriltag_array])
        self.pose = average_pose

    def get_kinematics(self) -> tuple[float, float, float]:
        """
        Gets current kinematics from robot
        @return: Kinematics from robot [xVelocity, yVelocity, rotVelocity]
        """
        return 0, 0, 0

    def get_pose(self) -> Pose:
        """
        Gets the calculated pose of the robot
        @return: Pose of robot
        """
        return self.pose

    def get_robot_mode(self) -> str:
        """
        Gets the mode input by the driver
        @return: String describing mode two options are "Manual" or "Auto"
        """
        return "Manual"

    def set_robot_output(self, kinematics: tuple[float, float, float]) -> None:
        """
        Sets the output of the robot
        @param kinematics: A tuple representing robot movement [xVelocity, yVelocity, rotVelocity]
        """
        print(f"Robot Output:\nxVel - {kinematics[0]}\nyVel - {kinematics[1]}\nrotVel - {kinematics[2]}")

    def get_team_color(self) -> str:
        """
        Gets the team color of the robot
        @return: Team color: "Red" or "Blue", the default will be red
        """
        return "Red"

    def get_game_time(self) -> float:
        """
        Gets the current time of the game.
        @return: Current time into match (seconds), this value will be counting up
        """
        return time.time() - self.end_time
