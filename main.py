import time
from operator import attrgetter

import vision_processing

cameras = [vision_processing.Camera.from_list(camera) for camera in vision_processing.GameField.cameras]
object_detection = vision_processing.DynamicObjectProcessing()

communications = vision_processing.NetworkCommunication()

while True:
    dynamic_objects = []
    reference_points = []
    timestamp = time.time()

    # Processing frames
    for camera in cameras:
        camera.update_frame()
        dynamic_objects.extend(object_detection.get_dynamic_objects(camera))
        reference_points.extend(vision_processing.ReferencePoint.from_apriltags(camera))

    if reference_points:
        communications.send_pose(max(reference_points, key=attrgetter("decision_margin")).robot_pose)

    communications.send_objects(dynamic_objects)

    # Printing FPS
    fps = 1 / (time.time() - timestamp)
    print(f"Cycle was successful.\nFPS: {round(fps, 3)}")
