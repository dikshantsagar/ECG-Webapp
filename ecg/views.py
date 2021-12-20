from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .forms import UploadFileForm
import pickle
import numpy as np
import pandas as pd
import json
import glob

import tensorflow as tf
from tensorflow.keras.models import load_model
import tensorflow.keras.backend as K
import shap
from numba import cuda 

from .utils import get_prediction, get_shap, plot_shap

def home(request):
    print(tf.config.list_physical_devices('GPU'))
    return render(request,'index.html')

@csrf_exempt
def handle_uploaded_file(f):
    with open('static/data/uploadedtest.csv', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

@csrf_exempt
def upload(request):


    if request.method == 'POST':

        form = UploadFileForm(request.POST, request.FILES)
        
        if form.is_valid():

            handle_uploaded_file(request.FILES['file'])

        else:
            form = UploadFileForm()
            

    return render(request, 'index.html')


def predict(request):

    
    class_dict = {0:'Conduction Disturbance',1:'Hypertrophy',2:'Myocardial Infarction',3:'Normal ECG',4:'ST/T change'}

    x = np.loadtxt("static/data/uploadedtest.csv", delimiter=",")
    x = x.transpose(1, 0)                              # transpose matrix
    x = np.expand_dims(x, axis=(0, -1))                # Add another channel on left and right  
    pred = get_prediction(x)[0]
    shap = np.array(get_shap(x))

    pred_class_indexes = [int(i) for i in np.where(pred == 1)[0]]
    
    classes = [class_dict[i] for i in pred_class_indexes]
    

    x = np.squeeze(x,axis=(0,-1))
    shap = np.squeeze(shap,axis=1)

    x_axis = [i/100 for i in range(1000)]
    paths = []
    leads = ['I', 'II', 'III', 'AVL', 'AVR', 'AVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
    for ind in pred_class_indexes:
        path = []
        for lead_num in range(12):
            pth = plot_shap(x_axis, x[lead_num], shap[ind][lead_num], lead_num, ind)
            path.append(pth)
            
        
        paths.append(zip(path,leads))

    
    device = cuda.get_current_device()
    device.reset()
    
    return render(request, 'result.html',{'iterator': paths, 'class':classes} ) 