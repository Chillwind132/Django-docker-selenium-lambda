from django.http import HttpResponse
from django.shortcuts import render
from .forms import InputForm
import subprocess
import os
from django.views.generic import CreateView
from .models import Data_sc
import re
import boto3
import mimetypes
from django.http import FileResponse
from django.shortcuts import redirect
import json
import time
#def index(request):
#    return HttpResponse("Hello Geeks")

s3_client = boto3.client('s3')
s3_bucket = "stg-uploaded-screenshots-lambda"
output_files = "/tmp"

class data_createview(CreateView):
    model = Data_sc
    fields = ('input_field')

# Create your views here.
def index(request):
    var_name = 'hello'

    output = []
    context = {}
    context['form'] = InputForm()
    
    print(request.POST)
    results = request.POST.getlist('input_url')
    try:
        results_list = results[0].split("\r\n")
        for item in results_list:
            output.append(item.strip())
        print () #output is a list of final urls to convert

        connector(output)
        context['done_flag'] = '1'

    except Exception as e:
        pass
    return render(request, "home.html", context)


def redirect_view(request):
    response = redirect('/redirect-success/')
    return response

def connector(site_url_list):

    urls = []

    for item in site_url_list:

        time.sleep(1)
        os.chdir("/home/mike/Desktop/Projects/Django-docker-selenium-lambda/docker-selenium-lambda")

        command = "sls invoke --function screenshot_proc --raw --data "  # Space is mandatory
        #site_url = "https://www.example.com/"

        
        sls_invoke = subprocess.Popen(command + item,
                                        shell=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        stdout, stderr = sls_invoke.communicate()

        url = re.findall('"([^"]*)"', str(stdout))
        urls.append(url[0])
        print(urls)
        
    
    if os.path.exists(output_files):
        pass
    else:
        os.mkdir(output_files)

    file_name = output_files + '/' + urls[0]
    s3_client.download_file(s3_bucket,urls[0],file_name)
    #response = download(file_name)

    ### write urls list to json
   
    jsonString = json.dumps(urls)
    with open('urls_data.json', 'w') as f:
         json.dump(jsonString, f)


    print("Done")

def download(request):
    data = {}
    tmp = "/tmp/"
    path = '/tmp/Picture2022-07-22_14:04:26.767981'

    with open('urls_data.json', 'r') as f:
        d = json.load(f)
        

    print(data)
    for item in data:

        path = tmp + item
        if os.path.exists(path):
            with open(path, 'rb') as fh:
                mime_type, _ = mimetypes.guess_type(path)
                response = HttpResponse(fh, content_type=mime_type)
                response['Content-Disposition'] = "attachment; filename=test.png"

                #response = FileResponse(fh)

                return response
        
    
