from django.urls import path
from . import views
from . import forms

app_name = 'bahtzang'

FORMS = [("lookup", forms.CamperLookupForm),
         ("select", forms.CamperSelectForm),
         ("update", forms.ParentUpdateForm)]

urlpatterns = [
    path('', views.PreregisterWizard.as_view(FORMS))
]
