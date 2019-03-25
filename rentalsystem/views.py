from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic
from .forms import *


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/landing')
    return TemplateResponse(request, "home.html")

class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


def add_category(request):
    cat_objects = Category.objects.all().values()   # get all the category objects from model

    print(cat_objects)

    # render template, give it all the category objects
    return render(request, 'add_category.html', {'cat_objects': cat_objects})
