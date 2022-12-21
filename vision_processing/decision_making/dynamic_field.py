from .. import NetworkCommunication
from ..vision.robot import Robot
from ..vision.dyanmic_object import DynamicObject
from vision_processing.vision.reference_point import ReferencePoint
from vision_processing.constants import GameField


class DynamicField:
    """
    A class representing the field merged by multiple frames
    """
    def __init__(self, robot: Robot, communications: NetworkCommunication):
        """
        Creates a DynamicField object
        @param robot: Robot being used on the field
        @param communications: Data communications object
        """
        self.robot = robot
        self.field_boundary = GameField.field_boundary
        self.obstructions = GameField.dead_zones
        self.objects: list[DynamicObject] = []
        self.game_time = 0
        self.communications = communications

    def sync_with_robot(self, april_tag_data: list[ReferencePoint]) -> None:
        """
        Syncs all relevant data with the robot
        @param april_tag_data: List of reference points given by apriltags to be merged with pose
        @return: null
        """
        self.communications.set_apriltag_pose_data(april_tag_data)

        self.robot.pose = self.communications.get_pose()
        self.robot.velocity = self.communications.get_kinematics()[0:2]
        self.robot.angular_velocity = self.communications.get_kinematics()[2]

        self.robot.mode = self.communications.get_robot_mode()
        self.robot.color = self.communications.get_team_color()

        self.game_time = self.communications.get_game_time()

    def update_field(
            self,
            timestamp: float,
            april_tag_data: list[ReferencePoint],
            dynamic_objects: list[DynamicObject]
    ) -> None:
        """
        Class to update the field, communicates with robot and updates objects on field
        @param timestamp: Timestamp of collected data
        @param april_tag_data: List of reference points from apriltags
        @param dynamic_objects: Objects collected by cameras
        @return: null
        """
        self.sync_with_robot(april_tag_data)
        self.update_objects(dynamic_objects, timestamp)

    def update_objects(self, new_objects: list[DynamicObject], timestamp: float) -> None:
        """
        Updates all objects on the field
        @param new_objects: New objects on field
        @param timestamp: timestamp of collected data
        @return:
        """
        for obj in new_objects:
            obj.add_absolute_coordinates(self.robot.pose)

        for obj in self.objects:
            min_dist = 0.2
            update_index = -1
            for i in range(0, len(new_objects)):
                distance = abs(new_objects[i].absolute_coordinates - obj.predict(when=new_objects[i].timestamp))
                if distance < min_dist and obj.object_name == new_objects[i].object_name:
                    min_dist = distance
                    update_index = i
            if update_index == -1:
                obj.update(timestamp=timestamp)
            else:
                obj.update(other=new_objects[update_index])
                new_objects.pop(update_index)

        self.objects.extend(new_objects)
        self.objects = sorted(self.objects, key=lambda obj: obj.probability)
        self.clean_objects()

    def clean_objects(self):
        """
        Cleans the list of objects by removing objects that are outside boundaries, inside dead-zones, or have decayed
        probability. @return: null
        """
        for i in range(len(self.objects) - 1, -1, -1):
            delete = False

            if self.objects[i].probability < 0.1:
                delete = True
            if not GameField.field_boundary.is_inside(self.objects[i].absolute_coordinates):
                delete = True
            for box in GameField.dead_zones:
                if box.is_inside(self.objects[i].absolute_coordinates):
                    delete = True
            if delete:
                self.objects.pop(i)



