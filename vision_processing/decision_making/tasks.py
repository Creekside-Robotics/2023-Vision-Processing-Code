from vision_processing import DynamicObject, GameField, Translation
from vision_processing.vision.robot import Robot


class GameTask:
    key_points: Translation = Translation(0, 0)
    paths = []
    rating = 0

    def __init__(self, dynamic_object: DynamicObject, robot: Robot):
        self.dynamic_object = dynamic_object
        self.robot = robot

    def get_id(self):
        return self.dynamic_object.id

    def estimate_time(self):
        estimated_travel_distance = abs(self.dynamic_object.absolute_coordinates - self.robot.pose.translation) * 1.2
        estimated_travel_speed = GameField.robot_translational_speed * 0.9
        travel_time = estimated_travel_distance / estimated_travel_speed
        return travel_time


