import math
import pyapriltags
from ..constants import GameField
from camera import Camera
from ..utils import Pose
import cv2


class ReferencePoint:
    def __init__(self, poseToRobot: Pose, poseToField: Pose):
        poseToRobot.reverse()
        poseToRobot.realtive_to_pose(poseToField)
        self.robotPose = poseToRobot

    def estimatatedRobotPose(self) -> Pose:
        return self.robotPose
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
        x, y, z, theta, phi = self.getDataFromDetection()
        polar_coordinates = self.cartesianToPolarTranslation(x, y, z)
        cartesian_coordinates, theta, phi = self.offset3dPoseRelativeToRobot(polar_coordinates, theta, phi)
        return Pose(cartesian_coordinates[0], cartesian_coordinates[1], theta)

    def getDataFromDetection(self):
        x, y, z = self.detection.pose_t[2], -self.detection.pose_t[0], -self.detection.pose_t[1]
        theta, phi = self.detection.pose_R[0], self.detection.pose_R[1]
        return x, y, z, theta, phi
    
    def cartesianToPolarTranslation(self, x: float, y: float, z: float) -> list:
        return [
            math.sqrt(x**2 + y**2 + z**2), 
            math.atan(y/x), 
            math.atan(z/math.sqrt(x**2 + y**2))
        ]
    
    def offset3dPoseRelativeToRobot(self, polar_coordinates: list[float, float, float], theta: float, phi: float):
        theta, polar_coordinates[1] += self.camera.rotational_offset[0]
        phi, polar_coordinates[2] += self.camera.rotational_offset[1]

        cartesian_coordinates = [
            math.cos(polar_coordinates[1])*polar_coordinates[0] + self.camera.translational_offset[0],
            math.sin(polar_coordinates[1])*polar_coordinates[0] + self.camera.translational_offset[1],
            math.sin(polar_coordinates[2])*polar_coordinates[0]
        ]

        return cartesian_coordinates, theta, phi

    def getPoseRelativeToField(self):
        return GameField().reference_points.get(self.detection.tag_id)