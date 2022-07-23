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
import zipfile

s3_client = boto3.client('s3')
s3_bucket = "stg-uploaded-screenshots-lambda"
output_files = "/tmp"
error_string = "Error"

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

        time.sleep(0.2)
        os.chdir("/home/ubuntu/django-project/Django-docker-selenium-lambda/docker-lambda-selenium-backend")

        command = "sls invoke --function screenshot_proc --raw --data "  # Space is mandatory
        #site_url = "https://www.example.com/"

        
        sls_invoke = subprocess.Popen(command + item,
                                        shell=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        stdout, stderr = sls_invoke.communicate()

        if error_string in str(stdout):
            pass
        else:
            url = re.findall('"([^"]*)"', str(stdout))
            urls.append(url[0])
        print(stdout)
        print(stderr)

    for item in urls:

        file_name = output_files + '/' + item
        s3_client.download_file(s3_bucket,item,file_name)

    ### write urls list to json
   
    jsonString = json.dumps(urls)
    with open('urls_data.json', 'w') as f:
         json.dump(jsonString, f)

    print("Done")

def download(request):
    data = []
    data_updated = []
    tmp = "/tmp/"
    os.chdir("/home/ubuntu/django-project/Django-docker-selenium-lambda/docker-lambda-selenium-backend")
    with open('urls_data.json', 'r') as f:
        d = json.load(f)
        data_string = str(d) 
        cleaned_str = data_string.replace("[","").replace("]","").replace('"','').strip()
        data = cleaned_str.split(",")
    for item in data:

        upd = tmp + item.strip()
        data_updated.append(upd)

    with zipfile.ZipFile('out.zip', 'w') as zipMe:        
        for file_path in data_updated:

            name=str(file_path).replace("/tmp/","").strip()

            zipMe.write(file_path,arcname=name,compress_type=zipfile.ZIP_DEFLATED)   
            print("ZIPPED FILE")
        
    if os.path.exists('out.zip'):
        with open('out.zip', 'rb') as fh:
            mime_type, _ = mimetypes.guess_type('out.zip')
            response = HttpResponse(fh, content_type=mime_type)
            response['Content-Disposition'] = "attachment; filename=out.zip"
            print("ZIP SENT TO CLIENT!")

    return response #Return the final zip file to the client



        
    
