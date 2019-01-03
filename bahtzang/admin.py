from django.contrib import admin

from .models import Camp, Family

admin.site.register([Camp, Family])
