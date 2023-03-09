import time
from operator import attrgetter

from typing import List
import tracemalloc

import vision_processing


class PipelineRunner:
    def __init__(
            self,
            communications: vision_processing.NetworkCommunication = vision_processing.NetworkCommunication(),
            cameras: List[vision_processing.Camera] = (vision_processing.Camera.from_list(camera) for camera in vision_processing.GameField.cameras)
    ):
        self.communications = communications
        self.cameras = cameras
        self.object_detection = vision_processing.DynamicObjectProcessing()

    tracemalloc.start()
    def run(self, num_of_cycles: int = -1):
        cycle_count = 0
        while cycle_count != num_of_cycles:
            cycle_count += 1

            print(tracemalloc.get_traced_memory())

            dynamic_objects = []
            reference_points = []
            timestamp = time.time()

            # Processing frames
            for camera in self.cameras:
                # dynamic_objects.extend(self.object_detection.get_dynamic_objects(camera))
                print("Before" + str(tracemalloc.get_traced_memory()))
                reference_points.extend(vision_processing.ReferencePoint.from_apriltags(camera))
                print("After" + str(tracemalloc.get_traced_memory()))

            if reference_points:
                try:
                    self.communications.send_pose(max(reference_points, key=attrgetter("decision_margin")).robot_pose)
                except:
                    print("AprilTag not detected.")

            # self.communications.send_objects(dynamic_objects)

            # Printing FPS
            fps = 1 / (time.time() - timestamp)
            print(f"Cycle {cycle_count} was successful.\nFPS: {round(fps, 3)}")
