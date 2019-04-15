from django.shortcuts import render, redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic
from .forms import *
from .models import *


def index(request):
    if request.user.is_authenticated:
        return home(request)
    return landing(request)


def home(request):
    context = {
        'items': Item.objects.all(),
        'categories': Category.objects.all()
    }
    return render(request, "home.html", context)


def landing(request):
    return render(request, "landing.html")


def myjobs(request):
    current_id = request.user.id # gets current logged in staff ID
    jl_id = JobList.objects.get(staff_id = current_id) #get current staff joblist
    jobs = Job.objects.filter(job_list_id = jl_id) #get all jobs for joblist_id

    return render(request, "myjobs.html", {'jobs' : jobs})


def profile(request):
    return render(request, 'profile.html')

class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

class UserPostItem(generic.CreateView):
    model = Item
    fields = ['name', 'info', 'image']

def item_details(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'item_details.html', {'item': item})
