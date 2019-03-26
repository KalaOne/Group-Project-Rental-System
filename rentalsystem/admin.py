from django.contrib import admin
from rentalsystem import models
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username', 'role']


# sets up the category view in the admin page
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']
    fields = ('title', 'description')


# register the models with the admin site
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(models.Category, CategoryAdmin)
