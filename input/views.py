from django.http import HttpResponse
from django.shortcuts import render
from .forms import InputForm
import subprocess
import os
from django.views.generic import CreateView
from .models import Data_sc

#def index(request):
#    return HttpResponse("Hello Geeks")

class data_createview(CreateView):
    model = Data_sc
    fields = ('input_field')

# Create your views here.
def index(request):
    context = {}
    context['form'] = InputForm()
    print(request.POST)
    results = request.POST.getlist('input_url')
    try:
        connector(results[0])
    except Exception as e:
        pass
    return render(request, "home.html", context)

def connector(site_url):
    os.chdir("/home/mike/Desktop/Projects/docker-selenium-lambda")

    command = "sls invoke --function screenshot_proc --raw --data "  # Space is mandatory
    #site_url = "https://www.example.com/"

    
    sls_invoke = subprocess.Popen(command + site_url,
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
    stdout, stderr = sls_invoke.communicate()

    print(stdout)
    print("Done")