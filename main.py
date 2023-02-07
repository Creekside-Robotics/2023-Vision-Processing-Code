import time

import vision_processing


cameras = [vision_processing.Camera.from_list(camera) for camera in vision_processing.GameField.cameras]
object_detection = vision_processing.DynamicObjectProcessing()

communications = vision_processing.NetworkCommunication()

while True:
    dynamic_objects = []
    reference_points = None
    timestamp = time.time()

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