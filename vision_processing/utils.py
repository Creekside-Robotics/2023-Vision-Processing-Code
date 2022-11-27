import math
from typing import NamedTuple
from scipy import spatial
import statistics

class Pixel(NamedTuple):
    """A pixel coordinate on a camera"""
    x: int
    y: int
    
class Translation(NamedTuple):
    """The position of something on the field"""
    x: float
    y: float
    """Whether the coordinates are relative to the field or the camera"""

    def relative_to_pose(self, pose):
        polar_coordiates = (
            spatial.distance.seuclidean([0, 0], [self.x, self.y]),
            math.atan2(self.y, self.x)
        )

        polar_coordiates[1] += pose.rot

        self.x = math.cos(polar_coordiates[1]) * polar_coordiates[0] + pose.x,
        self.y = math.sin(polar_coordiates[1]) * polar_coordiates[0] + pose.y

class Pose:
    def __init__(self, translation: Translation, rot: float) -> None:
        self.translation = translation
        self.rot = rot
    
    def realtive_to_pose(self, pose):
        """
        Adds pose to current
        """
        self.translation.relative_to_pose(pose)
        self.rot += pose.rot
    
    def reverse(self):
        """
        Inverts pose
        """
        polar_coordiates = (
            spatial.distance.seuclidean([0, 0], [self.x, self.y]),
            math.atan2(self.y, self.x) + math.pi - self.rot
        )

        self.translation.x = polar_coordiates[0] * math.cos(polar_coordiates[1])
        self.translation.y = polar_coordiates[0] * math.sin(polar_coordiates[1])
        self.rot = -self.rot

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
