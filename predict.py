from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
import tensorflow as tf


model = load_model('model/medical_image_model.h5')


def predict_image(img_path):
    try:
        img = image.load_img(img_path, target_size=(150, 150))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0

        prediction = model.predict(img_array)[0][0]
        confidence = prediction * 100 if prediction > 0.5 else (1 - prediction) * 100
        label = "Pneumonia Detected" if prediction > 0.5 else "Normal"

   
        last_conv_layer = model.get_layer(index=-5)  # You may adjust this index
        grad_model = tf.keras.models.Model([model.inputs], [last_conv_layer.output, model.output])
        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_array)
            loss = predictions[:, 0]

        grads = tape.gradient(loss, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        heatmap = conv_outputs[0] @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        heatmap = np.maximum(heatmap, 0) / np.max(heatmap)

       
        img = cv2.imread(img_path)
        img = cv2.resize(img, (150, 150))
        heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
        heatmap = np.uint8(255 * heatmap)
        heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        superimposed = cv2.addWeighted(img, 0.6, heatmap_color, 0.4, 0)

  
        cam_path = img_path.replace('.jpg', '_cam.jpg').replace('.jpeg', '_cam.jpg')
        cv2.imwrite(cam_path, superimposed)

        return f"{label} ({confidence:.2f}%)", cam_path

    except Exception as e:
        return f"Prediction failed: {str(e)}", None
