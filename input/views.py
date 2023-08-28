from django.views.generic import CreateView
from .models import Data_sc
from django.http import HttpResponse
from django.shortcuts import render
from .forms import InputForm
from django.http import FileResponse
from django.shortcuts import redirect
from django.http import HttpResponse, Http404
from datetime import datetime, timedelta
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
import string
import random
import collections

s3_client = boto3.client('s3')
s3_bucket = "stg-uploaded-screenshots-lambda"
output_files = "/tmp"
error_string = "Error"
N = 20

local = "docker-lambda-selenium-backend"
prod =  "docker-lambda-selenium-backend"

def index(request):


    unique_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))

    request.session['id'] = unique_id
    print(request.session['id'])

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

    print('connector unique_id:', unique_id)

    urls = {}

    # Change directory to the docker-lambda-selenium-backend folder if it's already not there
    print(f"Current working directory: {os.getcwd()}")
    if prod in os.getcwd():
        pass
    else:
        print("Changing directory to: " + prod)
        os.chdir(prod)

    for item in site_url_list:

        time.sleep(0.2)
        # print current working directory
        print("Curent working directory: " + os.getcwd())
        

        if os.path.exists('data'):
            pass
        else:
            os.mkdir('data')

        command = "sls invoke --function screenshot_proc --raw --data "  # Space is mandatory
        # item = "https://www.example.com/"

        print(f"Executing command: {command} {item}")

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

            # Append a list of output files paths to later use for s3 data transfer

            urls.setdefault(unique_id, []).append(url[0])

        print(stdout)
        print(stderr)

    for value in urls[unique_id]:
    for value in urls[unique_id]:

        file_name = output_files + '/' + value
        s3_client.download_file(s3_bucket,value,file_name) # Download output files and save to /tmp
        file_name = output_files + '/' + value
        s3_client.download_file(s3_bucket,value,file_name) # Download output files and save to /tmp

    ### write urls list to json
    print(f"Current working directory: {os.getcwd()}")

    with open('data/urls_data' + unique_id + '.json', 'w') as f:
        
        json.dump(urls, f)
    print(f"File created at {os.path.abspath('data/urls_data' + unique_id + '.json')}")



def delete_old_files(directory, age_minutes=15):
    now = datetime.now()

    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_mtime < (now - timedelta(minutes=age_minutes)):
                os.remove(file_path)
                print(f"Deleted old file: {file_path}")

def download(request, unique_id=None):
    try:
        unique_id = request.session['id']
        print('download unique_id:', unique_id)

        data = []
        data_updated = []
        tmp = "/tmp/"

        # Read json file with urls_data
        json_file = f'data/urls_data{unique_id}.json'
        if not os.path.exists(json_file):
            raise FileNotFoundError(f"Json data file '{json_file}' not found")

        with open(json_file, 'r') as f:
            d = json.load(f)
            data = d[unique_id]

        for item in data:
            upd = os.path.join(tmp, item.strip())
            data_updated.append(upd)

        file_name = f'{unique_id}.zip'
        file_path_data = os.path.join('data', file_name)

        # Create the ZIP file
        with zipfile.ZipFile(file_path_data, 'w') as zip_me:
            for file_path in data_updated:
                name = os.path.basename(file_path)
                zip_me.write(file_path, arcname=name, compress_type=zipfile.ZIP_DEFLATED)
                print("ZIPPED FILE")

        # Delete files older than 15 minutes in the 'data' directory
        delete_old_files('data', age_minutes=15)

        # Transfer the ZIP file to the client
        if os.path.exists(file_path_data):
            with open(file_path_data, 'rb') as fh:
                mime_type, _ = mimetypes.guess_type(file_path_data)
                response = HttpResponse(fh, content_type=mime_type)
                response['Content-Disposition'] = f'attachment; filename={file_name}'
                print("ZIP SENT TO CLIENT")
                return response

        else:
            raise FileNotFoundError(f"ZIP file '{file_path_data}' not found")

    except Exception as e:
        print(f"Download function error: {str(e)}")
        raise Http404(f"Error: {str(e)}")  # Return a 404 error with a custom message if any error occurs
    

