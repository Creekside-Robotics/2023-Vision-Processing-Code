import math

import numpy as np
from scipy import interpolate

from vision_processing import DynamicObject, GameField, Translation
from vision_processing.vision.robot import Robot


class GameTask:
    key_points: list[Translation]
    key_dist: list[float]
    done_before = False
    spline_points = list[Translation]
    spline_rot = list[float]
    spline_dist = list[float]
    rating = 0

    def __init__(self, dynamic_object: DynamicObject, robot: Robot):
        self.dynamic_object = dynamic_object
        self.robot = robot
        self.key_points = [robot.pose.translation, dynamic_object.predict(delay=self.estimate_time())]

    def get_id(self):
        return self.dynamic_object.id

    def estimate_time(self):
        estimated_travel_distance = abs(self.dynamic_object.absolute_coordinates - self.robot.pose.translation) * 1.2
        estimated_travel_speed = GameField.robot_translational_speed * 0.9
        travel_time = estimated_travel_distance / estimated_travel_speed
        return travel_time

    def clean_key_points(self):
        if self.done_before:
            farthest_distance = self.spline_dist[self.get_closest_point(point=self.robot.pose.translation)]
            for i in range(len(self.key_dist) - 2, 1, -1):
                if self.key_dist[i] > farthest_distance:
                    self.key_dist.pop(i)
                    self.key_points.pop(i)
            self.key_dist.insert(-2, self.spline_dist[self.get_closest_point(point=self.robot.pose.translation)])
            self.key_points.insert(-2, self.spline_points[self.get_closest_point(point=self.robot.pose.translation)])

    def generate_spline(self, foresight: float = 1, final_rot: float=None):
        self.spline_points = []
        self.spline_rot = []
        self.spline_dist = []

        # x,y coordinates of contour points, not monotonically increasing
        x = np.array([point.x for point in self.key_points])
        y = np.array([point.y for point in self.key_points])

        # build a spline representation of the contour
        spline = interpolate.splprep([x, y], u=self.key_dist, s=0)

        # resample it at smaller distance intervals
        interp_d = np.linspace(self.key_dist[0], self.key_dist[-1], 50)
        interp_x, interp_y = interpolate.splev(interp_d, spline)

        for i in range(len(interp_d)):
            self.spline_dist.append(interp_d[i])
            self.spline_points.append(Translation(interp_x[i], interp_y[i]))

        for i in range(len(self.spline_dist)):
            if i == len(self.spline_dist) - 1:
                if final_rot is None:
                    self.spline_rot.append(self.spline_rot[-1])
                else:
                    self.spline_rot.append(final_rot)
                pass
            distance = self.spline_dist[i] + foresight
            closest_index = self.get_closest_point(distance=distance)
            angle = (self.spline_points[closest_index] - self.spline_points[i])
            self.spline_rot.append(angle)
        self.done_before = True

    def get_closest_point(self, distance: float = None, point: Translation = None):
        if distance is not None:
            closest_index = -1
            closest_distance = 1000
            for i in range(len(self.spline_dist)):
                if abs(self.spline_dist[i] - distance) < closest_distance:
                    closest_distance = abs(self.spline_dist[i] - distance)
                    closest_index = i
            return closest_index
        if point is not None:
            closest_index = -1
            closest_distance = 1000
            for i in range(len(self.spline_points)):
                if abs(self.spline_points[i] - point) < closest_distance:
                    closest_distance = abs(self.spline_points[i] - point)
                    closest_index = i
            return closest_index

    def is_done(self):
        is_translation_done = self.get_closest_point(point=self.robot.pose.translation) == len(self.spline_dist) - 1
        is_rotation_done = abs((self.robot.pose.rot - self.spline_rot[-1])%(2*math.pi))
        return is_rotation_done and is_translation_done

    def get_output(self, speed: float = 1, foresight: float = 0.5):
        if self.robot.mode == "Manual":
            return 0, 0, 0
        multiplier = speed / foresight
        robot_location = self.robot.pose.translation
        robot_angle = self.robot.pose.rot

        index_of_goal = self.get_closest_point(
            distance=(
                    self.spline_dist[self.get_closest_point(point=robot_location)] + foresight
            )
        )

        translational_velocity = self.spline_points[index_of_goal] - robot_location
        rotational_velocity_unbound = (self.spline_rot[index_of_goal] - robot_angle)
        rotational_velocity = np.arctan2(np.sin(rotational_velocity_unbound), np.cos(rotational_velocity_unbound))

        return translational_velocity.x, translational_velocity.y, rotational_velocity
