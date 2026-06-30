from django.contrib import admin
from .models import CareCircle, Membership

#Register the CareCirlce model in the admin page
admin.site.register(CareCircle)
admin.site.register(Membership)