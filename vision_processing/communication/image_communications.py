from cscore import CameraServer, CvSource


class ImageCommunications:
    def __init__(self, name: str, width: int = 1920, height: int = 1080):
        """
        Creates an object used to communicate video to the robot.
        @param name: Name of camera stream
        @param width: Width of camera stream, defaults to 1920
        @param height: Height of the camera stream, defaults to 1080
        """
        self.source: CvSource = CameraServer.putVideo(name, width, height)

    def put_frame(self, frame):
        """
        Adds a frame to the camera stream
        @param frame: CV frame to add to the camera stream
        @return: null
        """
        self.source.putFrame(frame)
