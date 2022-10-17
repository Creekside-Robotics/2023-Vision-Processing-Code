import numpy
import tensorflow as tf

keras_model = tf.keras.applications.MobileNetV2()

def preprocessImage(path):
    img = tf.keras.preprocessing.image.load_img(path, target_size=(224, 224))
    imgArray = tf.keras.preprocessing.image.img_to_array(img)
    imgArrayExpand = numpy.expand_dims(imgArray, axis=0)
    return tf.keras.applications.mobilenet.preprocess_input(imgArrayExpand)

def predictImage(model, preprocessedImage):
    prediction = model.predict(preprocessedImage)
    results = tf.keras.applications.imagenet_utils.decode_predictions(prediction)[0]
    classification = ("Unknown Quantity", 0)
    for result in results:
        if result[2] > classification[1] and result[2] > 0.1:
            classification = (result[1], result[2])
    return classification[0]

imagePath = input("Enter absolute path to image: ")
preprocessedImage = preprocessImage(imagePath)

print(f"This is an image of a {predictImage(keras_model, preprocessedImage)}.")
