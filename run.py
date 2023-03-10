import time
from operator import attrgetter

from typing import List

import vision_processing


class PipelineRunner:
    def __init__(
            self,
            communications: vision_processing.NetworkCommunication = vision_processing.NetworkCommunication(),
            cameras: List[vision_processing.Camera] = None
    ):
        self.communications = communications
        self.object_detection = vision_processing.DynamicObjectProcessing()

        if cameras is None:
            self.cameras = [
                vision_processing.Camera.from_list(camera)
                for camera in vision_processing.GameField.cameras
            ]

    def run(self, num_of_cycles: int = -1):
        cycle_count = 0
        while cycle_count != num_of_cycles:
            cycle_count += 1

            dynamic_objects = []
            reference_points = []
            timestamp = time.time()

            # Processing frames
            for camera in self.cameras:
                dynamic_objects.extend(self.object_detection.get_dynamic_objects(camera))
                reference_points.extend(vision_processing.ReferencePoint.from_apriltags(camera))

            if reference_points:
                try:
                    self.communications.send_pose(max(reference_points, key=attrgetter("decision_margin")).robot_pose)
                except:
                    print("AprilTag not detected.")

            self.communications.send_objects(dynamic_objects)

            # Printing FPS
            fps = 1 / ((time.time() - timestamp) or 1e-9)  # prevent divide-by-zero
            print(f"Cycle {cycle_count} was successful.\nFPS: {round(fps, 3)}")

if __name__ == "__main__":
    PipelineRunner().run()
