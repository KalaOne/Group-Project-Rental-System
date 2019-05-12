#import datetime
from django.db.models import Min, Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.views import generic
from .forms import *
from .models import *
from datetime import *
from django.utils.dateparse import parse_datetime



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

def getAverageRating(itemid):
    item = Item.objects.get(id = itemid)
    print("Item: ",item)

    related_transactions = Transaction.objects.filter(item_id = itemid)
    if related_transactions.count() > 0:
        avg_rating = 0
        num_ratings = 0
        for transaction in related_transactions:
            try:
                review = Reviews.objects.get(transaction_id = transaction.id)
                avg_rating = avg_rating + review.item_rating
                num_ratings = num_ratings + 1
            except:
                avg_rating = avg_rating + 0
        if num_ratings > 0:
            avg_rating = avg_rating/num_ratings
        else:
            avg_rating = 0
        return avg_rating
    else:
        return 0

def home(request):

    prices = getLowestPrices()
    item_objects = Item.objects.all()

    average_reviews = []
    for item in Item.objects.all():
        average_reviews.append(int(getAverageRating(item.id)))

    print(average_reviews)
    items_and_prices_and_ratings = zip(item_objects, prices, average_reviews)

    context = {
        'categories': Category.objects.all(),
        'items': items_and_prices_and_ratings
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

    average_reviews = []
    for item in Item.objects.all():
        average_reviews.append(int(getAverageRating(item.id)))

    prices = getLowestPrices()

    items_and_prices_and_ratings = zip(items, prices, average_reviews)
    context = {
        'items': items_and_prices_and_ratings,
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
        job.delivered_datetime = datetime.now()
        job.delivered = True

        job.job_list_id = None

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

def confirm_transaction(request):
    if(request.method == 'GET'):
        list_id = request.GET.get('listingid')
        list_details = ItemListing.objects.select_related('item_type_id').get(id = list_id)

        s_date = request.GET.get('start_date')
        e_date = request.GET.get('end_date')

        sDate = datetime.strptime(s_date, '%Y-%m-%d')
        eDate = datetime.strptime(e_date, '%Y-%m-%d')

        rent_period = eDate - sDate

        total_cost = rent_period.days * list_details.cost_per_day

        context = {
            'list_details' : list_details,
            'dates' : [s_date, e_date],
            'cost' : total_cost
        }


    print("HELLOOOOOO")
    print(s_date)

    return render(request, 'confirm_transaction.html', context)


def rent_item(request):
    if request.method == 'POST':
        # get job info from the post request (button press)
        s_date = request.POST.get('start_date')

        e_date = request.POST.get('end_date')

        listing_id = ItemListing.objects.get(id=request.POST.get('listing_id'))
        o_id = CustomUser.objects.get(id=request.POST.get('owner_id'))
        cost = request.POST.get('total_cost')
        r_id = CustomUser.objects.get(id=request.user.id)

        #Create Transaction
        transaction = Transaction.objects.create(total_cost = cost,
                                   start_date = s_date,
                                   end_date = e_date,
                                   item_id = listing_id,
                                   owner_id = o_id,
                                   renter_id = r_id)


        # # Create delivery job
        # Job.objects.create( transaction_id= transaction.id,
        #                     due_delivery_datetime = transaction.start_date,
        #                     cost_per_day = request.POST.get('i_cost'),
        #                     owner_id = user_id,
        #                     item_type_id = i_id)
        allocate_jobs()

    return render(request, 'order_confirmation.html')

def allocate_jobs():
    for job in Job.objects.all():
        # if job hasnt been allocated yet
        if job.job_list_id is None:
            print("JOB LIST ID IS NONE")
            could_deliver = []
            region = job.county
            print(region)
            # Find all staff in jobs region
            for staff in CustomUser.objects.all():
                if staff.region == region and staff.role == "S":
                    print("FOUND STAFF")
                    could_deliver.append(staff)

            # If there are drivers in that region
            if len(could_deliver) is not 0:

                print("!!!!!!!!!!!!!COULD DELIVER NOT 0!!!!!!!!!!!!!!!!")

                to_deliver = could_deliver[0]
                max_job_count = 0

                for staff in could_deliver:
                    job_count = 0
                    # find staff member with least number of jobs
                    for jobList in JobList.objects.all():
                        if jobList.staff_id is staff.id:
                            job_count = job_count + 1

                        if job_count > max_job_count:
                            max_job_count = job_count
                            to_deliver = staff

                print(to_deliver)
                job_list = JobList.objects.create(staff_id = to_deliver)

                setattr(job, 'job_list_id', job_list)
                job.save()







def jobstats(request):
    obj = []
    # if POST request then the jobstats page is being filtered
    if request.method == 'POST':
        region = request.POST.get('region')
        days = request.POST.get('days')
        print("Region from page is: " + str(region))
        # calculate the completed number of jobs
        if days == "1day":
            total_jobs_completed_count = Job.objects.filter(delivered_datetime__isnull = False, delivered_datetime__gte =(datetime.now() - datetime.timedelta(days=1)), county = region).count()
        elif days == "1 week":
            total_jobs_completed_count = Job.objects.filter(delivered_datetime__isnull = False, delivered_datetime__gte =(datetime.now() - datetime.timedelta(days=7)), county = region).count()
        elif days == "2 weeks":
            total_jobs_completed_count = Job.objects.filter(delivered_datetime__isnull = False, delivered_datetime__gte =(datetime.now() - datetime.timedelta(days=14)), county = region).count()
        elif days == "1 month":
            total_jobs_completed_count = Job.objects.filter(delivered_datetime__isnull = False, delivered_datetime__gte =(datetime.now() - datetime.timedelta(days=30)), county = region).count()
        else:
            total_jobs_completed_count = Job.objects.filter(delivered_datetime__isnull = False).count()
        if region != 'All':
            jobs = Job.objects.filter(delivered_datetime__isnull=False, county=region).order_by('-delivered_datetime')
        else:
            jobs = Job.objects.filter(delivered_datetime__isnull=False).order_by('-delivered_datetime')

        # calculate the completed jobs in past 7 days
        # total_jobs_comp_last_week = Job.objects.filter(delivered_datetime__isnull =False, delivered_datetime__gte =(datetime.datetime.now() - datetime.timedelta(days=7)), county = region).count()

        # calculate number of unallocated jobs
        unalloc_jobs_count = Job.objects.filter(job_list_id__isnull = True, county = region).count()
        unalloc_jobs = Job.objects.filter(job_list_id__isnull = True, county = region)


        # calulate number of undelivered jobs
        undelivered_jobs_count = Job.objects.filter(delivered_datetime__isnull = True, county = region).count()
        undelivered_jobs = Job.objects.filter(delivered_datetime__isnull = True, county = region, job_list_id__isnull = False).order_by('-due_delivery_datetime')

        context = {
            'total_jobs_completed_count': total_jobs_completed_count,
            # 'total_jobs_comp_last_week': total_jobs_comp_last_week,
            'nun_unalloc_jobs' : unalloc_jobs_count,
            'nun_undelivered_jobs' : undelivered_jobs_count,
            'searched_region' : region,
            'day_sort' : days,
            'jobs' : jobs,
            'unalloc_jobs' : unalloc_jobs,
            'undelivered_jobs' : undelivered_jobs
        }

    # if no POST request then show all job stats
    else:
        total_jobs_completed_count = Job.objects.filter(delivered_datetime__isnull=False).count()

        jobs = Job.objects.filter(delivered_datetime__isnull=False).order_by('-delivered_datetime')

        # calculate the completed jobs in past 7 days
        # total_jobs_comp_last_week = Job.objects.filter(delivered_datetime__isnull =False, delivered_datetime__gte =(datetime.datetime.now() - datetime.timedelta(days=7)), county = region).count()

        # calculate number of unallocated jobs
        unalloc_jobs_count = Job.objects.filter(job_list_id__isnull=True).count()
        unalloc_jobs = Job.objects.filter(job_list_id__isnull=True)

        # calulate number of undelivered jobs
        undelivered_jobs_count = Job.objects.filter(delivered_datetime__isnull=True).count()
        undelivered_jobs = Job.objects.filter(delivered_datetime__isnull=True,
                                              job_list_id__isnull=False).order_by('-due_delivery_datetime')

        context = {
            'total_jobs_completed_count': total_jobs_completed_count,
            # 'total_jobs_comp_last_week': total_jobs_comp_last_week,
            'nun_unalloc_jobs': unalloc_jobs_count,
            'nun_undelivered_jobs': undelivered_jobs_count,
            'searched_region': 'All',
            'day_sort': 'All time',
            'jobs': jobs,
            'unalloc_jobs': unalloc_jobs,
            'undelivered_jobs': undelivered_jobs
        }

    return render(request, 'jobstats.html', context)


def profile(request):
    return render(request, 'profile.html')

class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

def user_post_item(request):
    # items = ItemListing.objects.)
    items = Item.objects.all()
    context = {
        'items' : items
    }
    return render(request, "user_post_item.html", context)


def item_details(request):
    if request.method == 'POST':

        i_id = request.POST.get('dropdown_value') ##get the ID in dropdown
        item = Item.objects.get(id = i_id) ## gets the Item with that ID
        item_name = item.name ##gets that Item's name
        item_id = request.POST.get('dropdown_value')
        info = request.POST.get('info_field')
        cost= request.POST.get('cost')
        context = {
            'item_name' : item_name,
            'info' : info,
            'cost' : cost,
            'item_id' : i_id
        }
    return render(request, 'rentalsystem/post_item_details.html', context)

def post_item_complete(request):
    if request.method =='POST':
        i_id = Item.objects.get(id = request.POST.get('i_id'))
        user_id = CustomUser.objects.get(id=request.user.id)
        ItemListing.objects.create(title=request.POST.get('i_name'),
                                    additional_info = request.POST.get('i_info'),
                                    cost_per_day = request.POST.get('i_cost'),
                                    owner_id = user_id,
                                    item_type_id = i_id)

    return render(request, 'rentalsystem/post_item_complete.html')

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
    datetime.now()).select_related('item_id').order_by('start_date')

    # get all orders filtered to current user
    # use select_related to also query the item table (needed for item name)
    # filter by all orders with end date less than(lt) than today
    completed_orders = Transaction.objects.filter(renter_id = current_user_id, end_date__lt =
    datetime.now()).select_related('item_id').prefetch_related('reviews_set').order_by('start_date')

    # integration test - print all orders
    print("TEST: Printing current users orders:")
    print(current_orders)

    context = {
        'current_orders' : current_orders,
        'completed_orders': completed_orders
    }

    return render(request, 'myorders.html', context)

def is_listing_available(listing_id):
    print("is listing available?")

def item_listings(request):

    # get query from either type of request
    if request.method == 'POST':
        item_name = request.POST.get('query_name')
    if request.method == 'GET':
        item_name = request.GET.get('query_name')

    # get the right item details from the query
    item = Item.objects.filter(name=item_name).first()
    print("Item name found: " + str(item_name))

    # save item into context so it's detailed can be rendered
    context = {
        'item':item,
        }

    # will be POSTed if dates have been selected
    if request.method == 'POST':

        # get the start and end dates from the form
        s_date = request.POST.get('date_start')
        e_date = request.POST.get('date_end')

        print("Selecting items available between " + str(s_date) + " and " + str(e_date))
        print("HELLLLLOOOO")


        items = ItemListing.objects.filter(item_type_id = item.id)
        cost = 10

        # create context with all available item listings
        context = {
            'item': item,
            'item_listings': items,
            'dates' : [s_date, e_date],
            'cost' : cost
            }

        return render(request, "rentalsystem/itemListings.html", context)

    # if not POSTed then first time page has been loaded - no dates so
    # don't provide any items
    else:
        print('Not showing item listings yet: need dates')
        return render(request, "rentalsystem/itemListings.html", context)
