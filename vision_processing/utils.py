import math
import statistics
from typing import NamedTuple

from scipy import spatial


class Pixel(NamedTuple):
    """A pixel coordinate on a camera"""

    x: int
    y: int


class Translation(NamedTuple):
    """The position of something on the field, or the difference between two points"""

    x: float
    y: float

    def relative_to_pose(self, pose: "Pose") -> "Translation":
        polar_coordinates = (
            spatial.distance.euclidean([0, 0], [self.x, self.y]),
            math.atan2(self.y, self.x) + pose.rot,
        )

        x = math.cos(polar_coordinates[1]) * polar_coordinates[0] + pose.x
        y = math.sin(polar_coordinates[1]) * polar_coordinates[0] + pose.y
        return Translation(x, y)

    def __neg__(self) -> "Translation":
        return Translation(-self.x, -self.y)

    def __add__(self, other: "Translation") -> "Translation":  # vector addition
        if not isinstance(other, Translation):
            return NotImplemented

        x = self.x + other.x
        y = self.y + other.y
        return Translation(x, y)

    def __sub__(self, other: "Translation") -> "Translation":
        return -self + other

    def __mul__(self, other: float) -> "Translation":  # scaling
        return Translation(self.x * other, self.y * other)

    def __truediv__(self, other: float) -> "Translation":  # also scaling
        return Translation(self.x / other, self.y / other)

    @staticmethod
    def add(first, second: "Translation") -> "Translation":
        """Adds the components of the two translations together"""
        return first + second

    @staticmethod
    def scale(translation, scalar: float) -> "Translation":
        """Scales the translation"""
        return translation * scalar

    def reverse(self) -> "Translation":
        """Creates a new translation going in the opposite direction"""
        return -self

    def __abs__(self):
        return math.sqrt(self.x**2 + self.y**2)

    def push_away(self, other_translation: "Translation", distance):
        vector_difference = other_translation - self
        vector_distance = abs(vector_difference)
        if vector_distance > distance:
            return other_translation, False
        unit_vector = vector_difference / vector_distance
        final_translation = self + unit_vector * distance
        return final_translation, True


class Pose:
    def __init__(self, translation: Translation, rot: float) -> None:
        self.translation = translation
        self.rot = rot

    @property
    def x(self) -> float:
        """The x value of the pose's translation"""
        return self.translation.x

    @property
    def y(self) -> float:
        """The y value of the pose's translation"""
        return self.translation.y

    def relative_to_pose(self, pose: "Pose") -> "Pose":
        """
        Adds two poses together and returns it

        :param pose: The other pose to add
        :type pose: Pose
        :returns: The new pose
        :rtype: Pose
        """
        translation = self.translation.relative_to_pose(pose)
        rot = self.rot + pose.rot
        return Pose(translation, rot)

    def reverse(self) -> "Pose":
        """
        Creates a new pose with reversed orientation

        :returns: The new pose
        :rtype: Pose
        """
        polar_coordinates = (
            spatial.distance.euclidean([0, 0], [self.x, self.y]),
            math.atan2(self.y, self.x) + math.pi - self.rot,
        )

        x = polar_coordinates[0] * math.cos(polar_coordinates[1])
        y = polar_coordinates[0] * math.sin(polar_coordinates[1])
        rot = -self.rot

        return Pose(Translation(x, y), rot)

    @staticmethod
    def average_angles(angles: list[float]) -> float:
        """
        Returns the average of a list of angles
        """
        x = sum(math.cos(a) for a in angles)
        y = sum(math.sin(a) for a in angles)

        if x == 0 and y == 0:
            return 0

        return math.atan2(y, x)

    @classmethod
    def average_poses(cls, poses: list["Pose"]) -> "Pose":
        """
        Takes a list of poses and returns the average pose.
        """
        return cls(
            Translation(
                statistics.mean([pose.translation.x for pose in poses]),
                statistics.mean([pose.translation.y for pose in poses]),
            ),
            cls.average_angles([pose.rot for pose in poses]),
        )


class Box:
    def __init__(self, lower_limit: Translation, upper_limit: Translation):
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.center = (self.lower_limit + self.upper_limit) / 2
        self.radius = abs(self.lower_limit - self.center)

    def is_inside(self, point: Translation, radius: float = 0) -> bool:
        if self.lower_limit.x + radius <= point.x <= self.upper_limit.x - radius \
                and self.lower_limit.y + radius <= point.y <= self.upper_limit.y - radius:
            return True
        else:
            return False

    def push_inside(self, point: Translation, distance: float):
        change = False
        x = point.x
        y = point.y

        if point.x > self.upper_limit.x - distance:
            x = self.upper_limit.x - distance
            change = True

        if point.y > self.upper_limit.y - distance:
            y = self.upper_limit.y - distance
            change = True

        if point.x < self.lower_limit.x + distance:
            x = self.lower_limit.x + distance
            change = True

        if point.y < self.lower_limit.x + distance:
            y = self.lower_limit.x + distance
            change = True

        return Translation(x, y), change

    def push_outside(self, point: Translation, distance: float):
        return self.center.push_away(point, distance)


class _Counter:
    """A class that gives ever-increasing values, starting from any chosen number (defaults to 0)"""

    def __init__(self, start=0):
        self._val = start - 1  # decrease by one to have it start at the right value

    def next(self):
        """Increment the counter by one and return the next number"""
        self._val += 1
        return self._val


dynamic_object_counter = _Counter(start=3)
