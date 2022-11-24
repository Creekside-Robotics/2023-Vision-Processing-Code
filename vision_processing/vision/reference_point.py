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

        referencePoints = [
            cls(
                DetectionPoseInterpretation(camera, detection).getPoseRelativeToRobot(), 
                DetectionPoseInterpretation(camera, detection).getPoseRelativeToField()
            ) for detection in detections
        ]
        return referencePoints

class DetectionPoseInterpretation:
    def __init__(self, camera: Camera, detection: pyapriltags.Detection):
        self.camera = camera
        self.detection = detection

    def getPoseRelativeToRobot(self):
        # 3d pose realtive to camera
        x, y, z = self.detection.pose_t[2], -self.detection.pose_t[0], -self.detection.pose_t[1]
        theta, phi = self.detection.pose_R[0], self.detection.pose_R[1]

        # 3d translation (polar) relative to camera
        polar_coordinates = [
            math.sqrt(x**2 + y**2 + z**2), 
            math.atan(y/x), 
            math.atan(z/math.sqrt(x**2 + y**2))
        ]

        # 3d rotation relative to robot
        theta, polar_coordinates[1] += self.camera.rotational_offset[0]
        phi, polar_coordinates[2] += self.camera.rotational_offset[1]

        # 3d translation (cartesian) relative to robot
        cartisian_coordinates = [
            math.cos(polar_coordinates[1])*polar_coordinates[0] + self.camera.translational_offset[0],
            math.sin(polar_coordinates[1])*polar_coordinates[0] + self.camera.translational_offset[1],
            math.sin(polar_coordinates[2])*polar_coordinates[0]
        ]

        # 2d pose relative to robot
        poseRelativeToRobot = Pose(cartisian_coordinates[0], cartisian_coordinates[1], theta)
        return poseRelativeToRobot

    def getPoseRelativeToField(self):
        return GameField().reference_points.get(self.detection.tag_id)