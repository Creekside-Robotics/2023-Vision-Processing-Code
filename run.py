import time
from operator import attrgetter

import vision_processing
import testing


class PipelineRunner:
    def __init__(self, test: bool = False):
        self.communications = vision_processing.NetworkCommunication()
        self.cameras = [vision_processing.Camera.from_list(camera) for camera in vision_processing.GameField.cameras]
        self.object_detection = vision_processing.DynamicObjectProcessing()

        if test:
            self.setup_testing()

    def setup_testing(self):
        self.communications = testing.TestNetworkCommunication()
        self.cameras = [vision_processing.Camera.from_list(vision_processing.GameField.test_camera)]

    def run(self, num_of_cycles: int = -1):
        cycle_count = 0
        while cycle_count != num_of_cycles:
            cycle_count += 1

            dynamic_objects = []
            reference_points = []
            timestamp = time.time()

            # Processing frames
            for camera in self.cameras:
                camera.update_frame()
                dynamic_objects.extend(self.object_detection.get_dynamic_objects(camera))
                reference_points.extend(vision_processing.ReferencePoint.from_apriltags(camera))

            if reference_points:
                self.communications.send_pose(max(reference_points, key=attrgetter("decision_margin")).robot_pose)

            self.communications.send_objects(dynamic_objects)

            # Printing FPS
            fps = 1 / (time.time() - timestamp)
            print(f"Cycle {cycle_count} was successful.\nFPS: {round(fps, 3)}")
