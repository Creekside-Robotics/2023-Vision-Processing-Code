import math
import cv2
import numpy as np


class Camera:
    def __init__(self, translational_offset, rotational_offset, resolution, fov, id):
        """
        Creates a camera object to be used for various functions
        :param translational_offset: tuple of length three - (x offset, y offset, z offset) all in robot coordinate system
        :param rotational_offset: tuple of length two - (pitch, yaw) radians
        :param resolution: tuple of length two - (x res, y res)
        :param fov: diagonal fov, radians
        :param id: camera id - for testing put the path to a video
        """
        self.input_feed = cv2.VideoCapture(id)
        self.translational_offset = translational_offset
        self.rotational_offset = rotational_offset
        self.center = (resolution[0]/2, resolution[1]/2)

        # If there was a vertical line, extending from the center of the image,
        # allowing us to see shape of the camera capture, this would be it's height in pixels.
        self.center_pixel_height = (1/math.atan(fov/2))*math.sqrt((resolution[0]/2)**2 + (resolution[1]/2)**2)

    def get_frame(self):
        """
        :return: latest frame from camera
        """
        return self.input_feed.grab()

    def get_dynamic_object(self, bbox_left, bbox_right):
        """
        Method for getting a ObjectSnapshot from a two bounding box coordinates
        :param bbox_left: tuple of length two, bottom left pixel coordinate of bounding box
        :param bbox_right: tuple of length two, bottom right pixel coordinate of bounding box
        :return: ObjectSnapshot object
        """
        left_robot_relative = self.grounded_point_translation(bbox_left)
        right_robot_relative = self.grounded_point_translation(bbox_right)
        perpendicular_connecting_slope = -(right_robot_relative[0] - left_robot_relative[0])/(right_robot_relative[1] - left_robot_relative[1])
        perpendicular_connecting_angle = math.atan(perpendicular_connecting_slope)

        bottom_center_robot_relative = (
            (left_robot_relative[0] + right_robot_relative[0])/2,
            (left_robot_relative[1] + right_robot_relative[1])/2
        )

        radius = math.sqrt(
            (left_robot_relative[0] - bottom_center_robot_relative[0]) ** 2
            +
            (left_robot_relative[1] - bottom_center_robot_relative[0]) ** 2
        )

        robot_relative_coordinates = (
            bottom_center_robot_relative[0] + radius*math.cos(perpendicular_connecting_angle),
            bottom_center_robot_relative[1] + radius*math.sin(perpendicular_connecting_angle)
        )





    def grounded_point_translation(self, pixel_coordinates):
        """
        Translates pixel coordinates into robot relative cartesian coordinates.
        :param pixel_coordinates: Takes a tuple of length 2, x and y in pixel coordinate system.
        :return: tuple of length 2, translation relative to robot
        """
        x_offset = -(pixel_coordinates[1] - self.center[1])
        y_offset = -(pixel_coordinates[0] - self.center[0])

        camera_relative_pitch = math.atan(x_offset/self.center_pixel_height)
        camera_relative_yaw = math.atan(y_offset/self.center_pixel_height)

        robot_relative_pitch = camera_relative_pitch + self.rotational_offset[0]

        pre_rotated_x = 1/math.tan(robot_relative_pitch) * -self.translational_offset[2]
        pre_rotated_y = math.tan(camera_relative_yaw) * math.sqrt(self.translational_offset[2]**2 + pre_rotated_x**2)
        pre_rotated_polar = (math.sqrt(pre_rotated_y**2+pre_rotated_x**2), math.atan(pre_rotated_y/pre_rotated_x))

        post_rotated_polar = (pre_rotated_polar[0], pre_rotated_polar[1] + self.rotational_offset[1])
        post_rotated_cartesian = (
            math.cos(post_rotated_polar[1]) * post_rotated_polar[0],
            math.sin(post_rotated_polar[1]) * post_rotated_polar[0]
        )
        return post_rotated_cartesian







