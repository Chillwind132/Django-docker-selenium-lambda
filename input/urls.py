from django.urls import path
#now import the views.py file into this code
from . import views
from .views import redirect_view, download

urlpatterns=[path('',views.index),
             path('redirect/', download, name="download")] # name = 'download' is linked in home.html for on-click form button action