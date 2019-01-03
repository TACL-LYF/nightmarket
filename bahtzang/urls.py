from django.urls import path
from . import views

app_name = 'bahtzang'

urlpatterns = [
    path('', views.preregistration_landing, name = 'preregistration_landing')
]
