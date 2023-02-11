from typing import List
from vision_processing import NetworkCommunication, Pose, DynamicObject


class TestNetworkCommunication(NetworkCommunication):
    def __init__(self):
        super().__init__()

    def send_objects(self, objs: List[DynamicObject]):
        print("\nObject Information")
        print(f"Name: {[obj.object_name for obj in objs]}")
        print(f"xPos: {[obj.absolute_coordinates[0] for obj in objs]}")
        print(f"yPos: {[obj.absolute_coordinates[1] for obj in objs]}")

    def send_pose(self, pose: Pose):
        print("\nRobot Position")
        print(f"xPos: {pose.x}")
        print(f"yPos: {pose.y}")
        print(f"rPos: {pose.rot}")
        print(f"Count: {self._counter.next()}")
