from django.urls import path
#now import the views.py file into this code
from . import views
from .views import  download

urlpatterns=[
    path('',views.index),
    path('download/<str:unique_id>/', views.download, name="download") # using the str converter for unique_id
]
