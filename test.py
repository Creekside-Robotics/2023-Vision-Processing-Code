import testing
import vision_processing

from run import PipelineRunner

pipeline = PipelineRunner(
    communications=testing.TestNetworkCommunication(),
    cameras=[vision_processing.Camera.from_list(vision_processing.GameField.test_camera)]
)
pipeline.run()
