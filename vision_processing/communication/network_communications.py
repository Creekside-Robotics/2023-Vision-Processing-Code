import networktables
from typing import Tuple, List

from vision_processing import ReferencePoint

from ..utils import Pose, Translation


class NetworkCommunication:
    def __init__(self):
        """
        NetworkCommunications is a class allowing the communication of robot data between the roborio and coproccesser
        via networktables
        """
        self.ntinst = networktables.NetworkTablesInstance.getDefault()
        self.ntinst.startClientTeam(8775)
        self.ntinst.startDSClient()
        self.robot_data_table = self.ntinst.getTable("Robot Data")
        self.robot_output_table = self.ntinst.getTable("Robot Output")
        self.game_data_table = self.ntinst.getTable("Game Data")

    def set_apriltag_pose_data(self, apriltag_array: List[ReferencePoint]) -> None:
        """
        Sends pose data from a list of reference points over networktables
        @param apriltag_array: List of apriltag reference points
        """
        average_pose = Pose.average_poses([tag.robot_pose for tag in apriltag_array])
        self.robot_data_table.getEntry("AprilTag Pose").setDoubleArray(
            (average_pose.translation.x, average_pose.translation.y, average_pose.rot)
        )

    def get_kinematics(self) -> Tuple[float, float, float]:
        """
        Gets current kinematics from robot
        @return: Kinematics from robot [xVelocity, yVelocity, rotVelocity]
        """
        return self.robot_data_table.getEntry("Kinematics").getDoubleArray((0, 0, 0))

    def get_pose(self) -> Pose:
        """
        Gets the calculated pose of the robot
        @return: Pose of robot
        """
        pose_tuple = self.robot_data_table.getEntry("Fused Pose").getDoubleArray(
            (0, 0, 0)
        )
        return Pose(Translation(pose_tuple[0], pose_tuple[1]), pose_tuple[2])

    def get_robot_mode(self) -> str:
        """
        Gets the mode input by the driver
        @return: String describing mode two options are "Manual" or "Auto"
        """
        return self.robot_output_table.getEntry("Mode").getString("Manual")

    def set_robot_output(self, kinematics: Tuple[float, float, float]) -> None:
        """
        Sets the output of the robot
        @param kinematics: A tuple representing robot movement [xVelocity, yVelocity, rotVelocity]
        """
        self.robot_output_table.getEntry("Output").setDoubleArray(kinematics)

    def get_team_color(self) -> str:
        """
        Gets the team color of the robot
        @return: Team color: "Red" or "Blue", the default will be red
        """
        return self.game_data_table.getEntry("Team Color").getString("Red")

    def get_game_time(self) -> float:
        """
        Gets the current time of the game.
        @return: Current time into match (seconds), this value will be counting up
        """
        return self.game_data_table.getEntry("Game Time").getDouble(0)
