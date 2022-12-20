from cscore import CameraServer, CvSource

from vision_processing import ImageCommunications
from cv2 import imshow


class TestImageCommunications(ImageCommunications):
    def __init__(self, name: str):
        super().__init__(name)
        self.name = name

    def put_frame(self, frame):
        """
        Adds a frame to the camera stream
        @param frame: CV frame to add to the camera stream
        @return: null
        """
        imshow(self.name, frame)
