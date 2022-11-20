import cv2
import numpy as np
from pupil_apriltags import Detection, Detector

from ..utils import Pixel

DETECTOR_OPTIONS = dict(families="tag16h5")
DETECT_OPTIONS: dict = dict(tag_size=0.2)


class AprilTag:
    def __init__(self, detection: Detection):
        self.detection = detection

    @property
    def center(self) -> Pixel:
        """The center of the detected tag"""
        return Pixel(*self.detection.center)

    @property
    def corners(self) -> list[Pixel]:
        """The corners of the detected tag"""  # todo better specify the order of the corners
        return [Pixel(*corner) for corner in self.detection.corners]

    @property
    def tag_id(self) -> int:
        """The id of the detected tag"""
        return self.tag_id

    @classmethod
    def from_image(
        cls, image: np.ndarray, camera_params: tuple = None
    ) -> list["AprilTag"]:
        """
        Create a new Apriltag from an image

        :param image: The image to create from, as a numpy array
        :type image: np.ndarray
        :param camera_params: The camera information to pass to the detection.
        Should be a tuple of (focal_length x, focal_length y, focal_center x, focal_center y).
        For a Camera instance, focal_length should be `self.center_pixel_height` and focal_center should be `self.center`
        :type camera_params: tuple
        :return: The Apriltag instance based off the image
        :rtype: AprilTag
        """
        if not isinstance(image, np.ndarray):
            raise TypeError(
                f"image must be an instance of np.ndarray, not {image.__class__.__name__!r}"
            )

        if len(image.shape) == 3:
            # Convert colored images to greyscale, since that's what the detector wants
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        detector = Detector(**DETECTOR_OPTIONS)

        detect_options = DETECT_OPTIONS.copy()
        if camera_params:
            detect_options["camera_params"] = camera_params
            detect_options["estimate_tag_pose"] = True

        # The detector lies about the return value, it should be a list
        detections: list[Detection] = detector.detect(image, **detect_options)  # noqa

        return [cls(detection) for detection in detections]
