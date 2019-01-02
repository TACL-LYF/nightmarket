from django.urls import path
from . import views

urlpatterns = [
    path('', views.preregistration_landing, name = 'preregistration_landing')
]
