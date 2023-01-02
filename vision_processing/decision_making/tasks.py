import math

import numpy as np
from scipy import interpolate

from ..vision import DynamicObject, Robot
from ..utils import Translation
from ..constants import GameField


class GameTask:
    def __init__(self, dynamic_object: DynamicObject, robot: Robot):
        """
        Class representing task that con be completed by the robot
        @param dynamic_object: Object task revolves around
        @param robot: Robot
        """
        self.dynamic_object = dynamic_object
        self.robot = robot
        self.key_points = [
            robot.pose.translation,
            dynamic_object.predict(delay=self.estimate_time()),
        ]
        self.key_dist: np.ndarray = np.array([])
        self.done_before = False
        self.spline_points: list[Translation] = []
        self.spline_rot: list[float] = []
        self.spline_dist: list[float] = []
        self.rating = 0

    @property
    def id(self):
        """
        Gets task id
        @return: task id
        """
        return self.dynamic_object.id

    def estimate_time(self) -> float:
        """
        Estimates the time to complete the task
        @return: task time
        """
        estimated_travel_distance = (
            abs(self.dynamic_object.absolute_coordinates - self.robot.pose.translation)
            * 1.2
        )
        estimated_travel_speed = GameField.robot_translational_speed * 0.9
        travel_time = estimated_travel_distance / estimated_travel_speed
        return travel_time

    def clean_key_points(self):
        """
        Cleans up the key points contained within the task
        @return: None
        """
        if self.done_before:
            self.key_points = [
                self.spline_points[
                    self.get_closest_point(point=self.robot.pose.translation)
                ],
                self.dynamic_object.predict(delay=self.estimate_time())
            ]
        else:
            self.key_points = [
                self.robot.pose.translation,
                self.dynamic_object.predict(delay=self.estimate_time())
            ]

    def generate_spline(self, foresight: float = 1, final_rot: float = None):
        """
        Generates a spline using the object's key points
        @param foresight: how far ahead the robot should be facing, defaults to 1
        @param final_rot: final rotation of the robot, keep optional if you do not want to control
        @return: None
        """
        self.spline_points = []
        self.spline_rot = []
        self.spline_dist = []

        spline_degree = 3
        if len(self.key_points) <= 3:
            spline_degree = len(self.key_points) - 1

        # x,y coordinates of contour points, not monotonically increasing
        x = np.array([point.x for point in self.key_points])
        y = np.array([point.y for point in self.key_points])

        # build a spline representation of the contour
        spline = interpolate.splprep([x, y], u=self.key_dist, k=spline_degree)[0]

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
                break
            distance = self.spline_dist[i] + foresight
            closest_index = self.get_closest_point(distance=distance)
            angle = (self.spline_points[closest_index] - self.spline_points[i]).angle_of()
            self.spline_rot.append(angle)
        self.done_before = True

    def get_closest_point(
        self, distance: float = None, point: Translation = None
    ) -> int:
        """
        Gets the closest point on spline to input position or distance
        @param distance: distance along path
        @param point: current position
        @return: index of closest point on spline
        """
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

    def is_done(self) -> bool:
        """
        Returns if the task is done
        @return: whether the task is done, bool
        """
        is_translation_done = (
            self.get_closest_point(point=self.robot.pose.translation)
            == len(self.spline_dist) - 1
        )
        if self.dynamic_object.object_name == "Ball":
            is_translation_done = abs(self.robot.pose.translation - self.dynamic_object.absolute_coordinates) < self.robot.size

        is_rotation_done = abs((self.robot.pose.rot - self.spline_rot[-1]) % (2 * math.pi)) < math.pi / 6
        return is_rotation_done and is_translation_done

    def get_output(
        self, speed: float = 1, foresight: float = 0.5
    ) -> tuple[float, float, float]:
        """
        @param speed: Speed of robot
        @param foresight: Distance ahead that robot is moving to
        @return: kinematic tuple (xVel, yVel, rotVel)
        """
        if self.robot.mode == "Manual":
            return 0, 0, 0
        multiplier = speed / foresight
        robot_location = self.robot.pose.translation
        robot_angle = self.robot.pose.rot

        index_of_goal = self.get_closest_point(
            distance=(
                self.spline_dist[self.get_closest_point(point=robot_location)]
                + foresight
            )
        )

        translational_velocity = (
            self.spline_points[index_of_goal] - robot_location
        ) * multiplier
        rotational_velocity_unbound = self.spline_rot[index_of_goal] - robot_angle
        rotational_velocity = np.arctan2(
            np.sin(rotational_velocity_unbound), np.cos(rotational_velocity_unbound)
        )

        return translational_velocity.x, translational_velocity.y, rotational_velocity
