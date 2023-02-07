import time
import math

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

while True:
    dynamic_objects = []
    timestamp = time.time()
    reference_point = None

    # Processing frames
    for camera in cameras:
        camera.update_frame()
        dynamic_objects.extend(object_detection.get_dynamic_objects(camera))
        reference_point = vision_processing.ReferencePoint.from_apriltags(camera)

    if reference_point is not None:
        communications.send_pose(reference_point.robot_pose)

    communications.send_objects(dynamic_objects)

    # Printing FPS
    fps = 1 / (time.time() - timestamp)
    print(f"Cycle was successful.\nFPS: {round(fps, 3)}")
