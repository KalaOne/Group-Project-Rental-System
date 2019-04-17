import datetime
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
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
    return render(request, "rentalsystem/home.html", context)

# Re renders home page with new 'context' after a search
def home_search(request):
    items = Item.objects.filter(name__icontains=request.GET['search_query'])

    # finds the category id for any category matching a search
    cat_id = Category.objects.filter(title__icontains=request.GET['search_query']).values_list('pk', flat=True)

    # TODO: need to fix this!
    #games_in_cat_id = ItemCategoryPair.objects.filter(category_id=cat_id).values_list('item_id', flat=True)

    #print("Games in category" + str(games_in_cat_id))
    print("Category=" + str(cat_id))
    context = {
        'items': items,
        'categories': Category.objects.all()
    }
    return render(request, "rentalsystem/home.html", context)


def landing(request):
    return render(request, "rentalsystem/landing.html")


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

    return render(request, "rentalsystem/myjobs.html", {'jobs' : jobs})


def profile(request):
    return render(request, 'profile.html')


class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'rentalsystem/signup.html'
