from __future__ import annotations

import collections
from time import time
from typing import TYPE_CHECKING

import cv2
import numpy as np
import tflite_runtime as tf

from ..utils import Pixel, Translation
from .dyanmic_object import DynamicObject

if TYPE_CHECKING:
    from .camera import Camera


class PBTXTParser:
    def __init__(self, path: str):
        self.path = path
        self.file: list[str] | None = None

    def parse(self):
        label_map = []
        with open(self.path, "r") as f:
            lines = f.readlines()
            for line in lines:
                label_map.append(line.strip("\n"))
        print(label_map)
        self.file = label_map

    def get_labels(self) -> list[str] | None:
        return self.file


class BBox(collections.namedtuple("BBox", ["xmin", "ymin", "xmax", "ymax"])):
    """Bounding box.
    Represents a rectangle which sides are either vertical or horizontal, parallel
    to the x or y axis.
    """

    xmin: float
    ymin: float
    xmax: float
    ymax: float

    def scale(self, sx, sy):
        """Returns scaled bounding box."""
        return BBox(
            xmin=sx * self.xmin,
            ymin=sy * self.ymin,
            xmax=sx * self.xmax,
            ymax=sy * self.ymax,
        )


class DynamicObjectProcessing:
    def __init__(self):
        print("Initializing TFLite runtime interpreter")
        try:
            model_path = "vision_processing/vision/tensorflow_resources/model.tflite"
            self.interpreter = tf.Interpreter(
                model_path,
                experimental_delegates=[
                    tf.load_delegate("libedgetpu.so.1")
                ],
            )
            self.hardware_type = "Coral Edge TPU"
        except:
            print("Failed to create Interpreter with Coral, switching to unoptimized")
            model_path = "vision_processing/vision/tensorflow_resources/unoptimized.tflite"
            self.interpreter = tf.Interpreter(model_path)
            self.hardware_type = "Unoptimized"

        self.interpreter.allocate_tensors()
        print("Getting labels")
        parser = PBTXTParser("vision_processing/vision/tensorflow_resources/map.txt")
        parser.parse()
        self.labels = parser.get_labels()
        self.frames = 0

    def get_dynamic_objects(self, cam: "Camera") -> list[DynamicObject]:
        start = time()
        # Acquire frame and resize to expected shape [1xHxWx3]
        frame_cv2 = cam.frame
        frame_time = cam.frame_time

        # input
        scale = self.set_input(frame_cv2)

        # run inference
        self.interpreter.invoke()

        dynamic_objects = []
        # output
        boxes, class_ids, scores, x_scale, y_scale = self.get_output(scale)
        for i in range(len(boxes)):
            if scores[i] > 0.5 or (self.labels[int(class_ids[i])] == "Ball" and scores[i] > 0.25):

                class_id = class_ids[i]
                if np.isnan(class_id):
                    continue

                class_id = int(class_id)
                if class_id not in range(len(self.labels)):
                    continue

                ymin, xmin, ymax, xmax = boxes[i]
                bbox = BBox(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax).scale(
                    x_scale, y_scale
                )
                ymin = int(bbox.ymin)
                xmin = int(bbox.xmin)
                ymax = int(bbox.ymax)
                xmax = int(bbox.xmax)
                relative_coordinates, radius = cam.get_dynamic_object_translation(
                    Pixel(xmin, ymax), Pixel(xmax, ymax)
                )
                dynamic_objects.append(
                    DynamicObject(
                        Translation(*relative_coordinates),
                        radius,
                        self.labels[class_id],
                        frame_time,
                    )
                )

        if self.frames % 100 == 0:
            print("Completed", self.frames, "frames. FPS:", (1 / (time() - start)))
        self.frames += 1
        return dynamic_objects

    def input_size(self) -> tuple[int, int]:
        """Returns input image size as (width, height) tuple."""
        _, height, width, _ = self.interpreter.get_input_details()[0]["shape"]
        return width, height

    def set_input(self, frame: np.ndarray) -> tuple[float, float]:
        """Copies a resized and properly zero-padded image to the input tensor.
        Args:
          frame: image
        Returns:
          Actual resize ratio, which should be passed to `get_output` function.
        """
        width, height = self.input_size()
        h, w, _ = frame.shape
        new_img = np.reshape(cv2.resize(frame, (320, 320)), (1, 320, 320, 3))
        self.interpreter.set_tensor(self.interpreter.get_input_details()[0]['index'], np.copy(new_img))
        return width / w, height / h

    def output_tensor(self, i):
        """Returns output tensor view."""
        tensor = self.interpreter.tensor(self.interpreter.get_output_details()[i]['index'])()
        return np.squeeze(tensor)

    def get_output(
        self, scale: tuple[float, float]
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float]:

        # Get all outputs from the model
        boxes = self.output_tensor(1)
        classes = self.output_tensor(3)
        scores = self.output_tensor(0)
        count = int(self.output_tensor(2))

        width, height = self.input_size()
        image_scale_x, image_scale_y = scale
        x_scale, y_scale = width / image_scale_x, height / image_scale_y
        return boxes, classes, scores, x_scale, y_scale
