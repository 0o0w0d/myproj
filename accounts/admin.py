from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin


# Register your models here.
@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    pass
