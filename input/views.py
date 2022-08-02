from django.views.generic import CreateView
from .models import Data_sc
from django.http import HttpResponse
from django.shortcuts import render
from .forms import InputForm
from django.http import FileResponse
from django.shortcuts import redirect
import subprocess
import os
import re
import boto3
import mimetypes
import json
import time
import zipfile
import string
import random
import collections

s3_client = boto3.client('s3')
s3_bucket = "stg-uploaded-screenshots-lambda"
output_files = "/tmp"
error_string = "Error"
N = 20

local = "/home/mike/Desktop/Projects/Django-docker-selenium-lambda/docker-lambda-selenium-backend"
prod =  "/home/ubuntu/django-project/Django-docker-selenium-lambda/docker-lambda-selenium-backend"

def index(request):


    unique_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))

    request.session['id'] = unique_id

    output = []
    context = {}
    context['form'] = InputForm()
    if request.method == 'POST':
        results = request.POST.getlist('input_url')
        try:
            results_list = results[0].split("\r\n")
            for item in results_list:
                clean_item = item
                if str(clean_item).strip() == '': # Check if there are any empty entries '', ignore if true
                    pass
                else:
                    output.append(item.strip()) # Output is a list of final urls to convert
            connector(output, unique_id)
            context['done_flag'] = '1' # Setting flag to trigger the download view
        except Exception as e:
            print(e)
    return render(request, "home.html", context)

def connector(site_url_list, unique_id):

    urls = {}

    for item in site_url_list:

        time.sleep(0.2)
        os.chdir(prod)

        if os.path.exists('data') is not True:
            os.mkdir('data')

        command = "sls invoke --function screenshot_proc --raw --data "  # Space is mandatory
        # item = "https://www.example.com/"

        sls_invoke = subprocess.Popen(command + str(item).strip(),
                                        shell=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        stdout, stderr = sls_invoke.communicate()

        if error_string in str(stdout).strip():
            print("ERROR STRING DETECTED!")
        else:
            url = re.findall('"([^"]*)"', str(stdout).strip())
            # Append a list of output files paths to later use for s3 data transfer

            urls.setdefault(unique_id, []).append(url[0])

        print(stdout)
        print(stderr)

    for value in urls[unique_id]:

        file_name = output_files + '/' + value
        s3_client.download_file(s3_bucket,value,file_name) # Download output files and save to /tmp

    ### write urls list to json

    with open('data/urls_data' + unique_id + '.json', 'w') as f:
        json.dump(urls, f)

def download(request):

    unique_id = request.session['id']

    data = []
    data_updated = []
    tmp = "/tmp/"
    os.chdir(prod)

    with open('data/urls_data' + unique_id + '.json', 'r') as f:
        d = json.load(f)
        data = d[unique_id]

    for item in data: # need to change since no need

        upd = tmp + item.strip()
        data_updated.append(upd)

    file_name = unique_id + '.zip'
    file_path_data = 'data/' + file_name

    if os.path.exists(file_path_data):
        with open(file_path_data, 'rb') as fh:
            mime_type, _ = mimetypes.guess_type(file_path_data)
            response = HttpResponse(fh, content_type=mime_type)
            response['Content-Disposition'] = "attachment; filename=out.zip"
            print("ZIP SENT TO CLIENT")
            return response  # Return the final zip file to the client
    else:
        with zipfile.ZipFile(file_path_data,'w') as zipMe:  # Zip the files before transfer
            for file_path in data_updated:

                name = str(file_path).replace("/tmp/", "").strip()

                zipMe.write(file_path,
                            arcname=name,
                            compress_type=zipfile.ZIP_DEFLATED)
                print("ZIPPED FILE")

        if os.path.exists(file_path_data):
            with open(file_path_data, 'rb') as fh:
                mime_type, _ = mimetypes.guess_type(file_path_data)
                response = HttpResponse(fh, content_type=mime_type)
                response['Content-Disposition'] = "attachment; filename=out.zip"
                print("ZIP SENT TO CLIENT")
                cleanup(unique_id)
                return response  # Return the final zip file to the client

def cleanup(unique_id):
    if os.path.exists('data/' + unique_id + '.zip'):
        os.remove('data/' + unique_id + '.zip')
    if os.path.exists('data/urls_data' + unique_id + '.json'):
        os.remove('data/urls_data' + unique_id + '.json')
