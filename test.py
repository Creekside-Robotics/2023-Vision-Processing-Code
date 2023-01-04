import time
import math
import cv2

import vision_processing
import testing


cameras = [
    vision_processing.Camera(
        (0.106, 0, 0.6606),
        (0, -math.pi / 7.5),
        650,
        "testing/testing_resources/HyperClock Test Video.mp4"
    )
]
object_detection = vision_processing.DynamicObjectProcessing()

communications = testing.TestNetworkCommunication()
image_communications = testing.TestImageCommunications("HyperClock UI")
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
writer = cv2.VideoWriter('testing/testing_resources/HyperClock Output Video.mp4', fourcc, 30, (350, 500))
robot = vision_processing.Robot()

field = vision_processing.DynamicField(robot, communications)
field_processor = vision_processing.FieldProcessing(field)
user_interface = vision_processing.UserInterface(field_processor)

while True:
    dynamic_objects = []
    reference_points = []
    timestamp = time.time()

    # Processing frames
    for camera in cameras:
        camera.update_frame()
        dynamic_objects.extend(object_detection.get_dynamic_objects(camera))
        reference_points.extend(vision_processing.ReferencePoint.from_apriltags(camera))

    # Updating field
    field.update_field(cameras[0].frame_time, reference_points, dynamic_objects)

    # Processing field and getting output
    field_processor.process_field()
    output = field_processor.get_output()

    # Sending output to robot
    communications.set_robot_output(output)

    # Generating and sending user interface
    interface_frame = user_interface.generate_field()
    image_communications.put_frame(interface_frame)
    writer.write(interface_frame)

    # Printing FPS
    fps = 1 / (time.time() - timestamp)
    print(f"Cycle was successful.\nFPS: {round(fps, 3)}")
