import re
from typing import TYPE_CHECKING

import cv2
import numpy as np
import tensorflow.lite as tflite
from PIL import Image

if TYPE_CHECKING:
    # This keeps pycharm from complaining about missing attributes
    import tensorflow._api.v2.lite as tflite

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

cv2.dnn

def load_labels(label_path):
    r"""Returns a list of labels"""
    with open(label_path) as f:
        labels = {}
        for line in f:
            m = re.match(r"(\d+)\s+(\w+)", line.strip())
            labels[int(m[1])] = m[2]
        return labels


def process_image(interpreter: tflite.Interpreter, image, input_index):
    r"""Process an image, Return a list of detected class ids and positions"""
    input_data = np.expand_dims(image, axis=0).astype(np.float32)  # expand to 4-dim

    # Process
    interpreter.set_tensor(input_index, input_data)
    interpreter.invoke()

    # Get outputs
    output_details = interpreter.get_output_details()

    # todo process the output

    # These all give 2d numpy arrays
    # scores = interpreter.get_tensor(0)
    # boxes = interpreter.get_tensor(1)
    # count = interpreter.get_tensor(2)
    # classes = interpreter.get_tensor(3)

    # Doesn't work, output_details is only 1 item long
    # positions = np.squeeze(interpreter.get_tensor(output_details[0]["index"]))
    # classes = np.squeeze(interpreter.get_tensor(output_details[1]["index"]))
    # scores = np.squeeze(interpreter.get_tensor(output_details[2]["index"]))



def __process_image(interpreter, image, input_index, k=3):
    r"""Process an image, Return top K result in a list of 2-Tuple(confidence_score, _id)"""
    input_data = np.expand_dims(image, axis=0).astype(np.float32)  # expand to 4-dim

    # Process
    interpreter.set_tensor(input_index, input_data)
    interpreter.invoke()

    # Get outputs
    output_details = interpreter.get_output_details()
    output_data = interpreter.get_tensor(output_details[0]["index"])
    print(output_data)
    output_data = np.squeeze(output_data)

    # Get top K result
    top_k = output_data.argsort()[-k:][::-1]  # Top_k index

    return [(_id, (output_data[_id] / 255.0)) for _id in top_k]


def display_result(result: list[dict], frame: np.ndarray, labels: dict[str, int]):
    r"""Display Detected Objects"""
    font = cv2.FONT_HERSHEY_SIMPLEX
    size = 0.6
    color = (255, 0, 0)  # Blue color
    thickness = 1

    # position = [ymin, xmin, ymax, xmax]
    # x * CAMERA_WIDTH
    # y * CAMERA_HEIGHT
    for obj in result:
        pos = obj["pos"]
        _id = obj["_id"]

        x1 = int(pos[1] * CAMERA_WIDTH)
        x2 = int(pos[3] * CAMERA_WIDTH)
        y1 = int(pos[0] * CAMERA_HEIGHT)
        y2 = int(pos[2] * CAMERA_HEIGHT)

        cv2.putText(frame, labels[_id], (x1, y1), font, size, color, thickness)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

    cv2.imshow("Object Detection", frame)


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

labels = load_labels(r"C:\Users\nathan\Documents\Vision-Processing-Code\labels.txt")


interpreter: tflite.Interpreter = tflite.Interpreter(
    r"lite-model_yolo-v5-tflite_tflite_model_1.tflite"
)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

input_shape = input_details[0]["shape"]
height = input_shape[1]
width = input_shape[2]

input_index = input_details[0]["index"]

floating_model = input_details[0]["dtype"] == np.float32

input_mean = 127.5
input_std = 127.5

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    ret: bool
    frame: np.ndarray

    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    # Our operations on the frame come here
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).resize(
        (width, height)
    )

    # input_data = np.expand_dims(image, axis=0)  # expand to 4-dim

    # if floating_model:
    #     input_data = (np.float32(input_data) - input_mean) / input_std

    # interpreter.set_tensor(input_details[0]["index"], input_data)
    # interpreter.invoke()
    #
    # output_data = interpreter.get_tensor(output_details[0]["index"])
    # results = np.squeeze(output_data)

    print(__process_image(interpreter, image, input_index))

    # top_k = results.argsort()[-5:][::-1]
    # for i in top_k:
    #     if floating_model:
    #         res = results[i]
    #         print(results[i])
    #         print("{:08.6f}: {}".format(float(results[i]), labels[i]))
    #         ...
    #     else:
    #         print("{:08.6f}: {}".format(float(results[i] / 255.0), labels[i]))

    # Process
    # interpreter.set_tensor(input_index, input_data)
    # interpreter.invoke()
    #
    # # Get outputs
    # output_details = interpreter.get_output_details()

    # Display the resulting frame
    cv2.imshow("frame", frame)

    if cv2.waitKey(1) == ord("q"):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
