from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .forms import UploadFileForm
import pickle
import numpy as np
import pandas as pd
import json
import glob
import os

import tensorflow as tf
from tensorflow.keras.models import load_model
import tensorflow.keras.backend as K
import shap
from numba import cuda 
import librosa
import gc
import math

import smtplib, ssl

from .utils import get_prediction, get_shap, plot_shap, top500

import datetime


def app(request):
    print("referrer",request.META.get('HTTP_REFERER'))
    print(tf.config.list_physical_devices('GPU'))
    physical_devices = tf.config.list_physical_devices('GPU')
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
    for plot in glob.glob('static/data/plots/*/*'):
        os.remove(plot)

    paths = glob.glob('static/data/samples/*')
    filenames = [i.split('/')[-1] for i in paths]
    

    return render(request,'index.html', {'samples':zip(filenames,paths)})

@csrf_exempt
def loginemail(request):

    OTP = ""
    if request.method == 'POST':

        email = request.POST.get('email')
        #print(email, request.POST)
        with open('static/data/users.txt','r') as fr:
            d = fr.read()
            if(email not in d):
                with open('static/data/users.txt','a+') as f:
                    f.write(email+'\n')

        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "ecg.sbilab@gmail.com" 
        with open('static/data/config.dat','r') as f:
            password = f.read()

        digits = "0123456789"
        
        for i in range(4) :
            OTP += digits[math.floor(np.random.random() * 10)]

        message = """\
        Subject: OTP For ECG Analyzer Login

        Your OTP for login is : """+str(OTP)
        
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, email, message)

    
        return render(request, 'home.html', {'otp':OTP})
        

def verifyotp(request):

    if request.method == 'POST':
        print(request.POST)
        otp_original = request.POST.get('otporig')
        otp_entered = request.POST.get('otpentered')

        if(otp_original == otp_entered):

            return redirect('/app')
@csrf_exempt
def review(request):

    if request.method == 'POST':

        print("review request",request.POST)
        resp = ''
        if request.POST.get('yes') == 'on':
            resp = 'Yes'
        else:
            resp = 'No'
        review = request.POST.get('text')

        with open('static/data/reviews.csv','a+') as f:
            f.write(resp+','+review+'\n')




    return JsonResponse({})
    



def index(request):
    OTP = ""
    print('referer',request.META.get('HTTP_REFERER'))
    print('method',request.method )
    if request.method == 'POST' and request.META.get('HTTP_REFERER') :

        email = request.POST.get('email')
        #print(email, request.POST)
        with open('static/data/users.txt','r') as fr:
            d = fr.read()
            if(email not in d):
                with open('static/data/users.txt','a+') as f:
                    f.write(email+'\n')

        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "ecg.sbilab@gmail.com" 
        with open('static/data/config.dat','r') as f:
            password = f.read()

        digits = "0123456789"
        
        for i in range(4) :
            OTP += digits[math.floor(np.random.random() * 10)]

        message = """\
        Subject: OTP For ECG Analyzer Login

        Your OTP for login is : """+str(OTP)
        
        
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, email, message)

    
        return render(request, 'home.html', {'otp':OTP})
    else:
        return render(request,'home.html')


@csrf_exempt
def handle_uploaded_file(f):
    
    with open('static/data/uploadedtest.csv', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    with open('static/data/collected/'+datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')+'.csv', 'wb+') as destination:
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

    #return render(request, 'result.html' ) 
        
    class_dict = {0:'Conduction Disturbance',1:'Hypertrophy',2:'Myocardial Infarction',3:'Normal ECG',4:'ST/T change'}

    try:
        x = np.loadtxt("static/data/uploadedtest.csv", delimiter="," )
    except:
        x = np.loadtxt("static/data/uploadedtest.csv")

    
    print(x.shape)

    
    if (request.method == 'POST'):
        rate = int(request.POST.get('rate') )
        
    else:
        rate = round(x.shape[0]/10)

    if (x.shape[0]/rate < 10.):
        return render(request,'index.html', {'error': 1})

    if(abs(x.mean()) > 10.):
        x = x/1000.  
                                           # bringing to range -5mv to +5mv if data.mean > 10
    
    x = x.transpose(1, 0)                              # transpose matrix

    
    resampled = []
    for i in x:
        resampled.append(librosa.resample(i,rate,100)[:1000])       #resample to 100Hz and crop 10 sec data
    x = np.array(resampled)

    x = np.expand_dims(x, axis=(0, -1))                # Add another channel on left and right 
    #print(x.shape) 
    pred, probs = get_prediction(x)
    print(pred)


    shap = np.array(get_shap(x))
    #shap = np.zeros((5, 1, 12, 1000))
    #print(shap)
    

    device = cuda.get_current_device()
    device.reset()


    
    

    pred_class_indexes = [int(i) for i in np.where(pred == 1)[0]]
  
    classes = [class_dict[i] for i in pred_class_indexes]
    probs = [round(probs[i]*100,2) for i in pred_class_indexes]
    

    probiter = zip(classes,probs)

    x = np.squeeze(x,axis=(0,-1))
    shap = np.squeeze(shap,axis=1)

    

    x_axis = [i/100 for i in range(1000)]
    paths = []
    leads = ['I', 'II', 'III', 'AVL', 'AVR', 'AVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
    print('Saving Figures Now!')
    for ind in pred_class_indexes:
        path = []
        shap[ind] = top500(shap[ind])
        for lead_num in range(12):
            pth = plot_shap(x_axis, x[lead_num], shap[ind][lead_num], lead_num, ind)
            path.append(pth)
            
            
        
        paths.append(zip(path,leads))
        
    
    
    
    
    return render(request, 'result.html',{'iterator': paths, 'classes': classes, 'probs':probiter} ) 