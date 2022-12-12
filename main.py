import time

from vision_processing import GameField, NetworkCommunication, Robot, DynamicObjectProcessing, DynamicField, \
    FieldProcessing, ReferencePoint

cameras = GameField.cameras
object_detection = DynamicObjectProcessing()

communications = NetworkCommunication()
robot = Robot()

field = DynamicField(robot, communications)
field_processor = FieldProcessing(field)

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

    # Printing FPS
    fps = 1 / (time.time() - timestamp)
    print(f"Cycle was successful.\nFPS: {round(fps, 3)}")
