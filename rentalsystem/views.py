import datetime
from django.shortcuts import render, redirect, get_object_or_404
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
    #For every Item
    lowest_prices = []
    for item in Item.objects.all():
        #get all ItemListings
        price = 1000000
        if ItemListing.objects.filter(item_type_id=item.id):
            print(ItemListing.objects.all())
            for item_listing in ItemListing.objects.filter(item_type_id=item.id):
                if item_listing.cost_per_day < price:
                    price = item_listing.cost_per_day
        else:
            price = None
        lowest_prices.append(price)
        print(lowest_prices)
    item_objects = Item.objects.all()
    prices = lowest_prices

    items_and_prices = zip(item_objects,prices)

    context = {
        'categories': Category.objects.all(),
        'items': items_and_prices
    }
    return render(request, "home.html", context)

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
    # if POST request then the jobstats page is being filtered
    if request.method == 'POST':
        region = request.POST.get('region')

        print("Region from page is: " + str(region))
        # calculate the completed number of jobs
        total_jobs_completed_count = Job.objects.filter(delivered_datetime__isnull = False, county = region).count()

        # calculate the completed jobs in past 7 days
        total_jobs_comp_last_week = Job.objects.filter(delivered_datetime__isnull = False, delivered_datetime__gte = (datetime.datetime.now() - datetime.timedelta(days=7)), county = region).count()

        context = {
            'total_jobs_completed_count': total_jobs_completed_count,
            'total_jobs_comp_last_week': total_jobs_comp_last_week,
            'searched_region' : region
        }

    # if no POST request then show all job stats
    else:
        # calculate the completed number of jobs
        total_jobs_completed_count = Job.objects.filter(delivered_datetime__isnull = False).count()

        # calculate the completed jobs in past 7 days
        total_jobs_comp_last_week = Job.objects.filter(delivered_datetime__isnull = False, delivered_datetime__gte = (datetime.datetime.now() - datetime.timedelta(days=7))).count()

        context = {
            'total_jobs_completed_count': total_jobs_completed_count,
            'total_jobs_comp_last_week': total_jobs_comp_last_week,
            'searched_region' : 'All Regions'
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
