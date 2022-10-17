import cv2
import numpy as np

import tensorflow.lite as tflite
from PIL import Image


interpreter: tflite.Interpreter = tflite.Interpreter(
    r"lite-model_yolo-v5-tflite_tflite_model_1.tflite"
)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
input_index = input_details[0]["index"]
input_shape = input_details[0]["shape"]
height = input_shape[1]
width = input_shape[2]


cap = cv2.VideoCapture(0)
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize(
        (width, height)
    )

    input_data = np.expand_dims(image, axis=0).astype(np.float32)  # expand to 4-dim

    # Process
    interpreter.set_tensor(input_index, input_data)
    interpreter.invoke()

    output_details = interpreter.get_output_details()
    output_data = interpreter.get_tensor(output_details[0]["index"])[0]
    print(output_data)
    break