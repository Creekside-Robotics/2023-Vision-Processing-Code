import math
from typing import NamedTuple

from scipy import spatial
import statistics

class Pixel(NamedTuple):
    """A pixel coordinate on a camera"""

    x: int
    y: int


class Translation(NamedTuple):
    """The position of something on the field, or the difference between two points"""

    x: float
    y: float

    def relative_to_pose(self, pose: "Pose") -> "Translation":
        polar_coordiates = (
            spatial.distance.euclidean([0, 0], [self.x, self.y]),
            math.atan2(self.y, self.x) + pose.rot,
        )

        x = math.cos(polar_coordiates[1]) * polar_coordiates[0] + pose.x
        y = math.sin(polar_coordiates[1]) * polar_coordiates[0] + pose.y
        return Translation(x, y)

    def __add__(self, other: "Translation") -> "Translation":  # vector addition
        if not isinstance(other, Translation):
            return NotImplemented

        x = self.x + other.x
        y = self.y + other.y
        return Translation(x, y)

    def __mul__(self, other: float) -> "Translation":  # scaling
        return Translation(self.x * other, self.y * other)

    @staticmethod
    def add(first, second: "Translation") -> "Translation":
        """Adds the components of the two translations together"""
        return first + second

    @staticmethod
    def scale(translation, scalar: float) -> "Translation":
        """Scales the translation"""
        return translation * scalar


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
        polar_coordiates = (
            spatial.distance.euclidean([0, 0], [self.x, self.y]),
            math.atan2(self.y, self.x) + math.pi - self.rot,
        )

        x = polar_coordiates[0] * math.cos(polar_coordiates[1])
        y = polar_coordiates[0] * math.sin(polar_coordiates[1])
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
                statistics.mean([pose.translation.y for pose in poses])
            ),
            cls.average_angles([pose.rot for pose in poses])
        )
