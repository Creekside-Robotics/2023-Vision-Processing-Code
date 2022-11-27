import networktables
from vision_processing import ReferencePoint
from ..utils import Pose


class NetworkCommunication:
    def __init__(self):
        self.ntinst = networktables.NetworkTablesInstance.getDefault()
        self.ntinst.startClientTeam(8775)
        self.ntinst.startDSClient()
        self.robot_data_table = self.ntinst.getTable("Robot Data")
        self.robot_output_table = self.ntinst.getTable("Robot Output")
        self.game_data_table = self.ntinst.getTable("Game Data")

    def set_apriltag_pose_data(self, apriltag_array: list[ReferencePoint]) -> None:
        average_pose = Pose.average_poses([tag.estimatatedRobotPose() for tag in apriltag_array])
        self.robot_data_table.getEntry("AprilTag Pose").setDoubleArray((
            average_pose.translation.x,
            average_pose.translation.y,
            average_pose.rot
        ))

    def get_kinematics(self) -> tuple[float, float, float]:
        return self.robot_data_table.getEntry("Kinematics").getDoubleArray((0, 0, 0))

    def get_pose(self) -> tuple[float, float, float]:
        return self.robot_data_table.getEntry("Fused Pose").getDoubleArray((0, 0, 0))

    def get_robot_mode(self) -> str:
        return self.robot_output_table.getEntry("Mode").getString("Manual")

    def set_robot_output(self, kinematics: tuple[float, float, float]) -> None:
        self.robot_output_table.getEntry("Output").setDoubleArray(kinematics)

    def get_team_color(self) -> str:
        return self.game_data_table.getEntry("Team Color").getString("Red")

    def get_game_time(self) -> float:
        return self.game_data_table.getEntry("Game Time").getDouble(0)
