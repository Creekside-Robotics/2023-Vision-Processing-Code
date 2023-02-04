import networktables

from ..utils import Pose, _Counter
from ..vision.dyanmic_object import DynamicObject


class NetworkCommunication:
    def __init__(self):
        """
        NetworkCommunications is a class allowing the communication of robot data between the roborio and coproccesser
        via networktables
        """
        self.ntinst = networktables.NetworkTablesInstance.getDefault()
        self.ntinst.startClientTeam(8775)
        self.ntinst.startDSClient()
        self.objects_table = self.ntinst.getTable("Objects")
        self.pose_table = self.ntinst.getTable("Pose")
        self._counter = _Counter(0)

    def send_object(self, obj: DynamicObject):
        self.objects_table.putNumber("Name", obj.object_name)
        self.objects_table.putNumber("xPos", obj.absolute_coordinates[0])
        self.objects_table.putNumber("yPos", obj.absolute_coordinates[1])
        self.objects_table.putNumber("counter", self._counter.next())

    def send_pose(self, pose: Pose):
        self.pose_table.putNumber("xPos", pose.x)
        self.pose_table.putNumber("yPos", pose.y)
        self.pose_table.putNumber("rPos", pose.rot)
        self.pose_table.putNumber("Count", self._counter.next())
