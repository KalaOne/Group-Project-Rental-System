import datetime
from django.db.models import Min
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

def getLowestPrices():
    lowest_prices = []
    for item in Item.objects.all():
        #get all ItemListings
        min_price = 0
        if ItemListing.objects.filter(item_type_id=item.id):
            min_price = ItemListing.objects.filter(item_type_id=item.id).aggregate(Min('cost_per_day'))
        else:
            min_price = None
        lowest_prices.append(min_price)
    return lowest_prices

def home(request):

    prices = getLowestPrices()

    item_objects = Item.objects.all()


    items_and_prices = zip(item_objects,prices)

    context = {
        'categories': Category.objects.all(),
        'items': items_and_prices
    }
    return render(request, "home.html", context)

# Re renders home page with new 'context' after a search
def home_search(request):
    # if update button pressed
    if request.method == 'POST':
        print("POST request")
        catPk = request.POST.get('catPk')
        itemsInCategory = ItemCategoryPair.objects.filter(category_id=catPk)
        items = Item.objects.filter(id__in=itemsInCategory)
    else:
        items = Item.objects.filter(name__icontains=request.GET['search_query'])


        cat_id = Category.objects.filter(title__icontains=request.GET['search_query']).values_list('pk', flat=True)

    prices = getLowestPrices()
    items_and_prices = zip(items,prices)
    context = {
        'items': items_and_prices,
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
    jobs = Job.objects.filter(job_list_id = jl_id).order_by('-delivered_datetime')#get all jobs for joblist_id

    return render(request, "myjobs.html", {'jobs' : jobs})

def createTrans(request):
    if(request.method == 'GET'):
        list_id = request.GET.get('listingid')
        list_details = ItemListing.objects.select_related('item_type_id').get(id = list_id)

        context = {
            'list_details' : list_details
        }

    if (request.method == 'POST'):
        print("createTrans called with POST")
        Transaction.objects.create(item_id=Item.objects.get(name = "The Goonies: Adventure Card Game"),
                                   owner_id=CustomUser.objects.get(name = "Matthew Taylor"),
                                   renter_id=CustomUser.objects.get(username = request.user.username),
                                   total_cost=request.POST.get('cost'),
                                   start_date=request.POST.get('date'),
                                   end_date=request.POST.get('date1'))

    return render(request, 'create_transaction.html', context)


def jobstats(request):
    # if POST request then the jobstats page is being filtered
    if request.method == 'POST':
        region = request.POST.get('region')
        days = request.POST.get('days')
        print("Region from page is: " + str(region))
        # calculate the completed number of jobs
        if days == "1day":
            total_jobs_completed_count = Job.objects.filter(delivered_datetime__isnull =False, delivered_datetime__gte =(datetime.datetime.now() - datetime.timedelta(days=1)), county = region).count()
        elif days == "1 week":
            total_jobs_completed_count = Job.objects.filter(delivered_datetime__isnull =False, delivered_datetime__gte =(datetime.datetime.now() - datetime.timedelta(days=7)), county = region).count()
        elif days == "2 weeks":
            total_jobs_completed_count = Job.objects.filter(delivered_datetime__isnull =False, delivered_datetime__gte =(datetime.datetime.now() - datetime.timedelta(days=14)), county = region).count()
        elif days == "1 month":
            total_jobs_completed_count = Job.objects.filter(delivered_datetime__isnull =False, delivered_datetime__gte =(datetime.datetime.now() - datetime.timedelta(days=30)), county = region).count()
        else:
            total_jobs_completed_count = Job.objects.filter(delivered_datetime__isnull = False, county = region).count()


        # calculate the completed jobs in past 7 days
        # total_jobs_comp_last_week = Job.objects.filter(delivered_datetime__isnull =False, delivered_datetime__gte =(datetime.datetime.now() - datetime.timedelta(days=7)), county = region).count()

        # calculate number of unallocated jobs
        unalloc_jobs_count = Job.objects.filter(job_list_id__isnull = True, county = region).count()


        # calulate number of undelivered jobs
        undelivered_jobs_count = Job.objects.filter(delivered_datetime__isnull = True, county = region).count()

        context = {
            'total_jobs_completed_count': total_jobs_completed_count,
            # 'total_jobs_comp_last_week': total_jobs_comp_last_week,
            'unalloc_jobs' : unalloc_jobs_count,
            'undelivered_jobs' : undelivered_jobs_count,
            'searched_region' : region
        }

    # if no POST request then show all job stats
    else:
        # calculate the completed number of jobs
        total_jobs_completed_count = Job.objects.filter(delivered_datetime__isnull = False).count()

        # calculate the completed jobs in past 7 days
        total_jobs_comp_last_week = Job.objects.filter(delivered_datetime__isnull = False, delivered_datetime__gte
        = (datetime.datetime.now() - datetime.timedelta(days=7))).count()

        # calculate number of unallocated jobs
        unalloc_jobs_count = Job.objects.filter(job_list_id__isnull = True).count()

        # calulate number of undelivered jobs
        undelivered_jobs_count = Job.objects.filter(delivered_datetime__isnull = True).count()

        context = {
            'total_jobs_completed_count': total_jobs_completed_count,
            # 'total_jobs_comp_last_week': total_jobs_comp_last_week,
            'unalloc_jobs' : unalloc_jobs_count,
            'undelivered_jobs' : undelivered_jobs_count,
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

def leave_review(request):
    if request.method == 'POST':
        # get job id from the post request (button press)
        transactionpk = request.POST.get('transactionpk')
        transaction = Transaction.objects.filter(id=transactionpk).select_related('item_id').select_related('owner_id').first()
        context = {
            'transaction': transaction,
        }
    else:
        return redirect('/my_orders/')
    return render(request, 'rentalsystem/review.html', context)

def review_confirmation(request):
    if request.method == 'POST':
        if Reviews.objects.create(transaction_id=Transaction.objects.get(id=request.POST.get('transactionpk')),
                                  content=request.POST.get('review_message'),
                                  item_rating=request.POST.get('itemrating'),
                                  transaction_rating=request.POST.get('transactionrating'),
                                  left_by_user_id=CustomUser.objects.get(id=request.user.id)):
            print("Successfully added review...")
        else:
            print("Review not added successfully...")
            return render(request, 'rentalsystem/myorders.html')
    else:
        print("ERROR - adding new review")
        return render(request, 'rentalsystem/myorders.html')
    context = {
        'review': Reviews.objects.filter(transaction_id=Transaction.objects.get(id=request.POST.get('transactionpk'))).last()
    }
    return render(request, 'rentalsystem/reviewconfirmation.html', context)

def my_orders(request):
    current_user_id = request.user.id

    # integration test - print current users id
    print("TEST: Current user ID is: " + str(current_user_id))

    # get all orders filtered to current user
    # use select_related to also query the item table (needed for item name)
    # filter by all orders with end date greater/equal(gte) than today
    current_orders = Transaction.objects.filter(renter_id = current_user_id, end_date__gte =
    datetime.datetime.now()).select_related('item_id').order_by('start_date')

    # get all orders filtered to current user
    # use select_related to also query the item table (needed for item name)
    # filter by all orders with end date less than(lt) than today
    completed_orders = Transaction.objects.filter(renter_id = current_user_id, end_date__lt =
    datetime.datetime.now()).select_related('item_id').prefetch_related('reviews_set').order_by('start_date')

    # integration test - print all orders
    print("TEST: Printing current users orders:")
    print(current_orders)

    context = {
        'current_orders' : current_orders, 
        'completed_orders': completed_orders
    }

    return render(request, 'myorders.html', context)


def item_listings(request):
    item_name = request.GET.get('query_name')
    item = Item.objects.filter(name=item_name).first()
    print(item_name)
    items = ItemListing.objects.filter(item_type_id=item.id)

    print(items)


    context = {
    'item':item,
    'item_listings':items }

    return render(request, "rentalsystem/itemListings.html", context)
