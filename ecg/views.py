from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .forms import UploadFileForm
import pickle
import numpy as np
import pandas as pd
import json
import glob

from tensorflow.keras.models import load_model
import tensorflow.keras.backend as K
import shap

from .utils import get_prediction, get_shap, plot_shap

def home(request):
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


    class_dict = {0:'',1:'',2:'',3:'',4:''}

    x = np.loadtxt("static/data/uploadedtest.csv", delimiter=",")
    x = x.transpose(1, 0)                              # transpose matrix
    x = np.expand_dims(x, axis=(0, -1))                # Add another channel on left and right  
    pred = get_prediction(x)[0]
    shap = np.array(get_shap(x))

    pred_class_index = int(np.where(pred == 1)[0])

    x = np.squeeze(x,axis=(0,-1))
    shap = np.squeeze(shap,axis=1)

    x_axis = [i/100 for i in range(1000)]

    for lead_num in range(12):
        plot_shap(x_axis, x[lead_num], shap[pred_class_index][lead_num], lead_num)


    return render(request, 'result.html')