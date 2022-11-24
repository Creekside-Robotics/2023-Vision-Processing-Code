import math
import pyapriltags

from vision_processing.field.field import GameField
from .. import Camera
from ..utils import Pose
import cv2


class ReferencePoint:
    def __init__(self, poseToRobot: Pose, poseToField: Pose):
        self.poseToRobot = poseToRobot
        self.poseToField = poseToField

    @classmethod
    def from_apriltags(
        cls, camera: Camera
    ) -> list["ReferencePoint"]:
        """
        Create a List of ReferencePoint from an image
        :rtype ReferencePoint
        """
        detector = pyapriltags.apriltags.Detector(GameField.apriltag_family)
        image = cv2.cvtColor(camera.get_frame(), cv2.COLOR_BGR2GRAY)

        detections = detector.detect(
            image, 
            estimate_tag_pose=True, 
            camera_params=(
                camera.center_pixel_height, 
                camera.center_pixel_height, 
                camera.center.x, 
                camera.center.y
            ),
            tag_size=GameField.apriltag_size
        )

        def extractPoseFromDetection(detection):
            x, y, z = detection.pose_t[2], -detection.pose_t[0], -detection.pose_t[1]
            theta, phi = detection.pose_R[0], detection.pose_R[1]

            polar_coordinates = [
                math.sqrt(x**2 + y**2 + z**2), 
                math.atan(y/x), 
                math.atan(z/math.sqrt(x**2 + y**2))
            ]

            theta, polar_coordinates[1] += camera.rotational_offset[0]
            phi, polar_coordinates[2] += camera.rotational_offset[1]

            cartisian_coordinates = [
                math.cos(polar_coordinates[1])*polar_coordinates[0] + camera.translational_offset[0],
                math.sin(polar_coordinates[1])*polar_coordinates[0] + camera.translational_offset[1],
                math.sin(polar_coordinates[2])*polar_coordinates[0]
            ]

            poseRelativeToRobot = Pose(cartisian_coordinates[0], cartisian_coordinates[1], theta)
            poseRelativeToField = GameField().reference_points.get(detection.tag_id)

            return cls(poseRelativeToRobot, poseRelativeToField)

        referencePoints = map(extractPoseFromDetection(), detections) 
        return referencePoints