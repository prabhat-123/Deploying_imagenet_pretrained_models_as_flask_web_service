from __future__ import division,print_function
import numpy as np
import tensorflow as tf
import sys
import os
import glob
import re


from tensorflow.keras.applications.imagenet_utils import preprocess_input, decode_predictions
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

from flask import Flask,redirect,url_for,request,render_template
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer


# Define a Flask App
app = Flask(__name__)

# Load model
model_path = 'vgg19_imagenet_weights.h5'
model = load_model(model_path)
model.summary()
# model._make_predict_function()  #Necessary for imagenet weights


def model_predict(img_path,model):
    img = image.load_img(img_path,target_size=(224,224))

    # Preprocessing the image
    x = image.img_to_array(img)
    x = np.expand_dims(x,axis=0)

    # Be careful how your trained model deals with the input
    # otherwise, it won't make correct prediction!
    x = preprocess_input(x)

    preds = model.predict(x)
    return preds


@app.route('/',methods = ['GET'])
def index():
    # Main page
    return render_template('./index.html')


@app.route('/',methods=["POST","GET"])
def upload():
    if request.method=='POST':
        f = request.files['file']
        print(f)
        # Save the file to './uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(basepath,'uploads',secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = model_predict(file_path,model)

        # Process your result for human
        # pred_class = pred.argmax(axis=-1)
        pred_class = decode_predictions(preds,top=1)
        result = str(pred_class[0][0][1])
        return result
    else:
        return None

if __name__ == '__main__':
    app.run(debug=True)