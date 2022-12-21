import time
import cv2
import math

from testing import TestImageCommunications, TestNetworkCommunication
from vision_processing import GameField, Robot, DynamicObjectProcessing, DynamicField, \
    FieldProcessing, ReferencePoint, UserInterface, Camera

cameras = [
    Camera(
        (0.106, 0, 0.6606),
        (-math.pi / 6, 0),
        636,
        "testing/testing_resources/HyperClock Test Video.mp4"
    )
]
object_detection = DynamicObjectProcessing()

communications = TestNetworkCommunication()
image_communications = TestImageCommunications("HyperClock UI")
robot = Robot()

field = DynamicField(robot, communications)
field_processor = FieldProcessing(field)
user_interface = UserInterface(field_processor)

while True:
    dynamic_objects = []
    reference_points = []
    timestamp = time.time()

    # Processing frames
    for camera in cameras:
        dynamic_objects.extend(object_detection.get_dynamic_objects(camera))
        reference_points.extend(ReferencePoint.from_apriltags(camera))

    # Updating field
    field.update_field(timestamp, reference_points, dynamic_objects)

    # Processing field and getting output
    field_processor.process_field()
    output = field_processor.get_output()

    # Sending output to robot
    communications.set_robot_output(output)

    # Generating and sending user interface
    interface_frame = user_interface.generate_field()
    image_communications.put_frame(interface_frame)

    # Printing FPS
    fps = 1 / (time.time() - timestamp)
    print(f"Cycle was successful.\nFPS: {round(fps, 3)}")

    cv2.waitKey(0)
