from django.contrib import admin
from .models import User

#Register users model in the admin page
admin.site.register(User)