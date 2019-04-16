import datetime
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
    # if update button pressed
    if request.method == 'POST':
        # get job id from the post request (button press)
        jobpk = request.POST.get('jobpk')

        # get the job from the model using the primary key
        job = Job.objects.get(id = jobpk)

        # set datetime and boolean delivery status
        job.delivered_datetime = datetime.datetime.now()
        job.delivered = True

        # save object
        job.save()
        
    # create list of current users jobs to pass into template
    current_id = request.user.id # gets current logged in staff ID
    jl_id = JobList.objects.get(staff_id = current_id) #get current staff joblist
    jobs = Job.objects.filter(job_list_id = jl_id) #get all jobs for joblist_id

    return render(request, "myjobs.html", {'jobs' : jobs})


def jobstats(request):
    # calculate the completed number of jobs
    total_jobs_completed_count = Job.objects.filter(delivered_datetime__isnull = False).count()

    # calculate the completed jobs in past 7 days
    total_jobs_comp_last_week = Job.objects.filter(delivered_datetime__isnull = False, delivered_datetime__gte = (datetime.datetime.now() - datetime.timedelta(days=7))).count()

    context = {
        'total_jobs_completed_count': total_jobs_completed_count,
        'total_jobs_comp_last_week': total_jobs_comp_last_week
    }

    return render(request, 'jobstats.html', context)


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
    return render(request, 'rentalsystem/post_item_details.html', {'item': item})
