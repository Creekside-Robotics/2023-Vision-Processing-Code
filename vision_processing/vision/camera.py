import math
from time import time

import cv2
import numpy as np

from ..utils import Pixel, Translation


class Camera:
    def __init__(
        self,
        translational_offset: tuple[float, float, float],
        rotational_offset: tuple[float, float],
        focal_length: float,
        port_id,
    ):
        """
        Creates a camera object to be used for various functions
        :param translational_offset: tuple of length three - (x offset, y offset, z offset) all in robot coordinate system
        :type translational_offset: tuple[int, int, int]
        :param rotational_offset: tuple of length two - (pitch, yaw) radians
        :type rotational_offset: tuple[float, float]
        :param port_id: camera id - for testing put the path to a video
        :type port_id: Any
        """
        self.input_feed: cv2.VideoCapture = cv2.VideoCapture(port_id)
        self.translational_offset: tuple[float, float, float] = translational_offset
        self.rotational_offset: tuple[float, float] = rotational_offset
        self.frame: np.ndarray = self.input_feed.read()[1]
        self.center: Pixel = Pixel(self.frame.shape[1] // 2, self.frame.shape[0] // 2)
        self.frame_time = time()

        # If there was a vertical line, extending from the center of the image,
        # allowing us to see shape of the camera capture, this would be its height in pixels.
        self.center_pixel_height: float = focal_length

    @classmethod
    def from_list(cls, parameter_list: tuple) -> "Camera":
        """
        Returns a Camera object from a list of parameters in order to avoid circular import errors.
        @param parameter_list: List of parameters: [
            translational_offset: tuple[float, float, float],
            rotational_offset: tuple[float, float],
            focal_length: float,
            port_id
        ]
        @return: Camera from the list
        """
        return cls(
            parameter_list[0],
            parameter_list[1],
            parameter_list[2],
            parameter_list[3]
        )

    def update_frame(self) -> None:
        self.frame = self.input_feed.read()[1]
        self.frame_time = time()

    def get_dynamic_object_translation(
        self, bbox_left: Pixel, bbox_right: Pixel
    ) -> tuple[Translation[float, float], float]:
        """
        :param bbox_left: tuple of length two, bottom left pixel coordinate of bounding box
        :type bbox_left: Pixel
        :param bbox_right: tuple of length two, bottom right pixel coordinate of bounding box
        :type bbox_right: Pixel
        """
        left_robot_relative = self.grounded_point_translation(bbox_left)
        right_robot_relative = self.grounded_point_translation(bbox_right)
        perpendicular_connecting_angle = math.pi / 2 + math.atan2(
            right_robot_relative[1] - left_robot_relative[1],
            right_robot_relative[0] - left_robot_relative[0],
        )

        bottom_center_robot_relative = (
            (left_robot_relative[0] + right_robot_relative[0]) / 2,
            (left_robot_relative[1] + right_robot_relative[1]) / 2,
        )

        radius = (left_robot_relative[1] - bottom_center_robot_relative[1])

        robot_relative_coordinates = Translation(
            bottom_center_robot_relative[0]
            + radius * math.cos(perpendicular_connecting_angle),
            bottom_center_robot_relative[1]
            + radius * math.sin(perpendicular_connecting_angle),
        )

        return robot_relative_coordinates, radius

    def grounded_point_translation(
        self, pixel_coordinates: Pixel
    ) -> tuple[float, float]:
        """
        Translates pixel coordinates into robot relative cartesian coordinates.
        :param pixel_coordinates: Takes a tuple of length 2, x and y in pixel coordinate system.
        :return: tuple of length 2, translation relative to robot
        """
        pixel_y_offset = pixel_coordinates.y - self.center.y
        pixel_x_offset = pixel_coordinates.x - self.center.x

        camera_relative_pitch = math.atan2(-pixel_y_offset, self.center_pixel_height)
        camera_relative_yaw = math.atan2(-pixel_x_offset, self.center_pixel_height)

        robot_relative_pitch = camera_relative_pitch + self.rotational_offset[1]

        pre_rotated_x = (
            1 / math.tan(-robot_relative_pitch) * self.translational_offset[2]
        )
        pre_rotated_y = math.tan(camera_relative_yaw) * math.sqrt(
            self.translational_offset[2] ** 2 + pre_rotated_x**2
        )
        pre_rotated_polar = (
            math.sqrt(pre_rotated_y**2 + pre_rotated_x**2),
            math.atan2(pre_rotated_y, pre_rotated_x),
        )

        post_rotated_polar = (
            pre_rotated_polar[0],
            pre_rotated_polar[1] + self.rotational_offset[0],
        )
        post_rotated_cartesian = (
            math.cos(post_rotated_polar[1]) * post_rotated_polar[0],
            math.sin(post_rotated_polar[1]) * post_rotated_polar[0],
        )
        return post_rotated_cartesian
