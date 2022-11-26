import math
from typing import NamedTuple
from scipy import spatial


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
