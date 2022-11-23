import collections
from time import time
from dyanmic_object import DynamicObject
from camera import Camera
import tensorflow as tf
import numpy as np
import cv2

class PBTXTParser:
    def __init__(self, path):
        self.path = path
        self.file = None

    def parse(self):
        with open(self.path, 'r') as f:
            self.file = ''.join([i.replace('item', '') for i in f.readlines()])
            blocks = []
            obj = ""
            for i in self.file:
                if i == '}':
                    obj += i
                    blocks.append(obj)
                    obj = ""
                else:
                    obj += i
            self.file = blocks
            label_map = []
            for obj in self.file:
                obj = [i for i in obj.split('\n') if i]
                name = obj[2].split()[1][1:-1]
                label_map.append(name)
            self.file = label_map

    def get_labels(self):
        return self.file


class BBox(collections.namedtuple('BBox', ['xmin', 'ymin', 'xmax', 'ymax'])):
    """Bounding box.
    Represents a rectangle which sides are either vertical or horizontal, parallel
    to the x or y axis.
    """
    __slots__ = ()

    def scale(self, sx, sy):
        """Returns scaled bounding box."""
        return BBox(xmin=sx * self.xmin,
                    ymin=sy * self.ymin,
                    xmax=sx * self.xmax,
                    ymax=sy * self.ymax)


class DynamicObjectProcessing:
    def __init__(self):
        print("Initializing TFLite runtime interpreter")
        try:
            model_path = "tensorflow_resorces/model.tflite"
            self.interpreter = tf.lite.Interpreter(model_path,
                                                  experimental_delegates=[tf.lite.experimental.load_delegate('libedgetpu.so.1')])
            self.hardware_type = "Coral Edge TPU"
        except:
            print("Failed to create Interpreter with Coral, switching to unoptimized")
            model_path = "unoptimized.tflite"
            self.interpreter = tf.lite.Interpreter(model_path)
            self.hardware_type = "Unoptimized"

        self.interpreter.allocate_tensors()
        print("Getting labels")
        parser = PBTXTParser("tensorflow_resorces/map.pbtxt")
        parser.parse()
        self.labels = parser.get_labels()
        self.frames = 0

    def getDynamicObjects(self, cam):
        start = time()
        # Acquire frame and resize to expected shape [1xHxWx3]
        ret, frame_cv2 = cam.get_frame()
        if not ret:
            print("Image failed")
            return

        # input
        scale = self.set_input(frame_cv2)

        # run inference
        self.interpreter.invoke()

        dynamic_objects = []
        # output
        boxes, class_ids, scores, x_scale, y_scale = self.get_output(scale)
        for i in range(len(boxes)):
            if scores[i] > .5:

                class_id = class_ids[i]
                if np.isnan(class_id):
                    continue

                class_id = int(class_id)
                if class_id not in range(len(self.labels)):
                    continue

                ymin, xmin, ymax, xmax = boxes[i]
                bbox = BBox(xmin=xmin,
                            ymin=ymin,
                            xmax=xmax,
                            ymax=ymax).scale(x_scale, y_scale)
                ymin, xmin, ymax, xmax = int(bbox.ymin), int(bbox.xmin), int(bbox.ymax), int(bbox.xmax)
                relative_coordinates, radius = cam.get_dynamic_object_position((xmin, ymax), (xmax, ymin))
                dynamic_objects.append(DynamicObject(relative_coordinates, radius, self.labels[class_id]))

        if self.frames % 100 == 0:
            print("Completed", self.frames, "frames. FPS:", (1 / (time() - start)))
        self.frames += 1

    def input_size(self):
        """Returns input image size as (width, height) tuple."""
        _, height, width, _ = self.interpreter.get_input_details()[0]['shape']
        return width, height

    def set_input(self, frame):
        """Copies a resized and properly zero-padded image to the input tensor.
        Args:
          frame: image
        Returns:
          Actual resize ratio, which should be passed to `get_output` function.
        """
        width, height = self.input_size()
        h, w, _ = frame.shape
        new_img = np.reshape(cv2.resize(frame, (300, 300)), (1, 300, 300, 3))
        self.interpreter.set_tensor(self.interpreter.get_input_details()[0]['index'], np.copy(new_img))
        return width / w, height / h

    def output_tensor(self, i):
        """Returns output tensor view."""
        tensor = self.interpreter.get_tensor(self.interpreter.get_output_details()[i]['index'])
        return np.squeeze(tensor)

    def get_output(self, scale):
        boxes = self.output_tensor(0)
        class_ids = self.output_tensor(1)
        scores = self.output_tensor(2)

        width, height = self.input_size()
        image_scale_x, image_scale_y = scale
        x_scale, y_scale = width / image_scale_x, height / image_scale_y
        return boxes, class_ids, scores, x_scale, y_scale
