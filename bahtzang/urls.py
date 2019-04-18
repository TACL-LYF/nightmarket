from django.urls import path
from . import views

app_name = 'bahtzang'

urlpatterns = [
    path('', views.lookup, name='lookup'),
    path('select', views.select, name='select'),
    path('update', views.update, name='update'),
    path('donation', views.donation, name='donation'),
    path('payment', views.payment, name='payment'),
    path('confirm', views.confirm, name='confirm')
]
