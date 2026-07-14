from django.contrib import admin
from .models import CareCircle, Membership, SeniorProfile

admin.site.register(CareCircle) #Register the CareCirlce model in the admin page
admin.site.register(Membership) #Register the membership model in the admin page
admin.site.register(SeniorProfile) #Register the senior profile model in the admin page