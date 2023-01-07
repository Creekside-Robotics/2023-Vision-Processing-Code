from __future__ import annotations

import math

import cv2
import numpy
import dt_apritags as pyapriltags

from ..constants import GameField
from ..utils import Pose, Translation
from .camera import Camera


class ReferencePoint:
    def __init__(self, pose_to_robot: Pose, pose_to_field: Pose):
        robot_to_reference = pose_to_robot.reverse()
        robot_to_field = robot_to_reference.relative_to_pose(pose_to_field)
        self.robot_pose = robot_to_field

    @classmethod
    def from_apriltags(cls, camera: Camera) -> list["ReferencePoint"]:
        """
        Create a List of ReferencePoint from an image
        :rtype ReferencePoint
        """
        detector = pyapriltags.apriltags.Detector(GameField.apriltag_family)
        image = cv2.cvtColor(camera.frame, cv2.COLOR_BGR2GRAY)

        # noinspection PyTypeChecker
        detections = detector.detect(
            image,
            estimate_tag_pose=True,
            camera_params=(
                camera.center_pixel_height,
                camera.center_pixel_height,
                camera.center.x,
                camera.center.y,
            ),
            tag_size=GameField.apriltag_size,
        )

        reference_points = [
            cls(
                DetectionPoseInterpretation(
                    camera, detection
                ).get_pose_relative_to_robot(),
                DetectionPoseInterpretation(
                    camera, detection
                ).get_pose_relative_to_field(),
            )
            for detection in detections
            if detection.decision_margin > 10 and detection.tag_id in GameField.reference_points.keys()
        ]
        return reference_points


class DetectionPoseInterpretation:
    def __init__(self, camera: Camera, detection: pyapriltags.Detection):
        self.camera = camera
        self.detection = detection

    def get_pose_relative_to_robot(self) -> Pose:
        # 3d pose relative to camera
        x, y, z, theta, phi = self.get_data_from_detection()
        polar_coordinates = self.cartesian_to_polar_translation(x, y, z)
        cartesian_coordinates, theta, phi = self.offset_pose_relative_to_robot(
            polar_coordinates, theta, phi
        )
        return Pose(
            Translation(cartesian_coordinates[0], cartesian_coordinates[1]), theta
        )

    def get_data_from_detection(self) -> tuple[float, float, float, float, float]:

        x, y, z = (
            self.detection.pose_t[2],
            -self.detection.pose_t[0],
            -self.detection.pose_t[1],
        )
        theta, phi, zeta = DetectionPoseInterpretation.angles_from_rotational_matrix(self.detection.pose_R)
        return x, y, z, theta, phi

    @staticmethod
    def angles_from_rotational_matrix(rot_mat: numpy.ndarray) -> tuple[float, float, float]:
        phi = math.atan2(rot_mat[2][1], rot_mat[2][2])
        theta = -math.atan2(-rot_mat[2][0], math.sqrt(rot_mat[2][1]**2 + rot_mat[2][2]**2))
        zeta = -math.atan2(rot_mat[1][0], rot_mat[0][0])
        return theta, phi, zeta

    @staticmethod
    def cartesian_to_polar_translation(
        x: float, y: float, z: float
    ) -> list[float, float, float]:
        return [
            math.sqrt(x**2 + y**2 + z**2),
            math.atan2(y, x),
            math.atan2(z, math.sqrt(x**2 + y**2)),
        ]

    def offset_pose_relative_to_robot(
        self, polar_coordinates: list[float, float, float], theta: float, phi: float
    ) -> tuple[tuple[float, float, float], float, float]:
        theta += self.camera.rotational_offset[0]
        polar_coordinates[1] += self.camera.rotational_offset[0]

        phi += self.camera.rotational_offset[1]
        polar_coordinates[2] += self.camera.rotational_offset[1]

        cartesian_coordinates = (
            math.cos(polar_coordinates[1]) * polar_coordinates[0]
            + self.camera.translational_offset[0],
            math.sin(polar_coordinates[1]) * polar_coordinates[0]
            + self.camera.translational_offset[1],
            math.sin(polar_coordinates[2]) * polar_coordinates[0],
        )

        return cartesian_coordinates, theta, phi

    def get_pose_relative_to_field(self) -> Pose | None:
        return GameField.reference_points.get(self.detection.tag_id)
