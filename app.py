from __future__ import division,print_function
import numpy as np
import tensorflow as tf
import sys
import os
import glob
import re

# This block of code is used if you are going to deploy your model in Nvidi GPU if you don't have it then you can skip these codes

from tensorflow.compat.v1 import ConfigProto
from tensorflow.python.keras.backend import set_session


tf.keras.backend.clear_session()
config = tf.compat.v1.ConfigProto(gpu_options = 
                         tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.9)
)
config.gpu_options.allow_growth = True
session = tf.compat.v1.Session(config=config)
tf.compat.v1.keras.backend.set_session(session)

# Upto here 


from tensorflow.keras.applications.inception_v3 import preprocess_input, decode_predictions
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

from flask import Flask,redirect,url_for,request,render_template
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer


# Define a Flask App
app = Flask(__name__)

# Load model
# graph = tf.get_default_graph()
model_path = 'inception_imagenet_weights.h5'
model = load_model(model_path)
model.summary()
model._make_predict_function()  #Necessary for imagenet weights 
# If model._make_predict_funciton() throws you error then you can discard this line and comment it.


def model_predict(img_path,model):
		img = image.load_img(img_path,target_size=(299,299))
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
		return render_template('./predict.html',result=result)
	else:
		return render_template('./index.html')

if __name__ == '__main__':
	app.run(debug=True)





