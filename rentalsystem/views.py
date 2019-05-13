# import datetime
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
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

User = get_user_model()

def getLowestPrices():
    lowest_prices = []
    for item in Item.objects.all():
        # get all ItemListings
        min_price = 0
        if ItemListing.objects.filter(item_type_id=item.id):
            min_price = ItemListing.objects.filter(item_type_id=item.id).aggregate(Min('cost_per_day'))
        else:
            min_price = None
        lowest_prices.append(min_price)
    return lowest_prices


def getAverageRating(itemid):
    item = Item.objects.get(id=itemid)
    print("Item: ", item)

    related_transactions = Transaction.objects.filter(item_id=itemid)
    if related_transactions.count() > 0:
        avg_rating = 0
        num_ratings = 0
        for transaction in related_transactions:
            try:
                review = Reviews.objects.get(transaction_id=transaction.id)
                avg_rating = avg_rating + review.item_rating
                num_ratings = num_ratings + 1
            except:
                avg_rating = avg_rating + 0
        if num_ratings > 0:
            avg_rating = avg_rating / num_ratings
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
        job = Job.objects.get(id=jobpk)

        # set datetime and boolean delivery status
        job.delivered_datetime = datetime.now()
        job.delivered = True

        job.job_list_id = None

        # save object
        job.save()

    # create list of current users jobs to pass into template
    current_id = request.user.id  # gets current logged in staff ID
    jl_id = JobList.objects.get(staff_id=current_id)  # get current staff joblist
    jobs = Job.objects.filter(job_list_id=jl_id).order_by('-delivered_datetime')  # get all jobs for joblist_id

    return render(request, "myjobs.html", {'jobs': jobs})


def createTrans(request):
    if (request.method == 'GET'):
        list_id = request.GET.get('listingid')
        list_details = ItemListing.objects.select_related('item_type_id').get(id=list_id)

        context = {
            'list_details': list_details
        }

    if (request.method == 'POST'):
        print("createTrans called with POST")
        Transaction.objects.create(item_id=Item.objects.get(name="The Goonies: Adventure Card Game"),
                                   owner_id=CustomUser.objects.get(name="Matthew Taylor"),
                                   renter_id=CustomUser.objects.get(username=request.user.username),
                                   total_cost=request.POST.get('cost'),
                                   start_date=request.POST.get('date'),
                                   end_date=request.POST.get('date1'))

    return render(request, 'create_transaction.html', context)


def confirm_transaction(request):
    if (request.method == 'GET'):
        list_id = request.GET.get('listingid')
        list_details = ItemListing.objects.select_related('item_type_id').get(id=list_id)

        s_date = request.GET.get('start_date')
        e_date = request.GET.get('end_date')

        sDate = datetime.strptime(s_date, '%Y-%m-%d')
        eDate = datetime.strptime(e_date, '%Y-%m-%d')

        rent_period = eDate - sDate

        total_cost = rent_period.days * list_details.cost_per_day

        context = {
            'list_details': list_details,
            'dates': [s_date, e_date],
            'cost': total_cost
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

        # Create Transaction
        transaction = Transaction.objects.create(total_cost=cost,
                                                 start_date=s_date,
                                                 end_date=e_date,
                                                 item_id=listing_id,
                                                 owner_id=o_id,
                                                 renter_id=r_id)

        customer = CustomUser.objects.get(id=request.user.id)
        # Create delivery job
        Job.objects.create( due_delivery_datetime = transaction.start_date,
                            transaction_id = transaction,
                            address1 = customer.address.address1,
                            address2 = customer.address.address2,
                            address3 = customer.address.address3,
                            address4 = customer.address.address4,
                            address5 = customer.address.address5,
                            county = customer.region,
                            post_code = customer.address.post_code
                            )

        # Create return delivery job
        Job.objects.create( due_delivery_datetime = transaction.end_date,
                            transaction_id = transaction,
                            address1 = customer.address.address1,
                            address2 = customer.address.address2,
                            address3 = customer.address.address3,
                            address4 = customer.address.address4,
                            address5 = customer.address.address5,
                            county = customer.region,
                            post_code = customer.address.post_code
                            )
                            
        # Try to allocate any unallocated jobs
        allocate_jobs()

    return render(request, 'order_confirmation.html')


# Checks unallocated jobs and allocates staff member with the least
# amount of current jobs to that job, iff they are in the same region
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
                job_list = JobList.objects.create(staff_id=to_deliver)

                setattr(job, 'job_list_id', job_list)
                job.save()

                email = job.transaction_id.renter_id.email

                # send_mail(
                #     'Your board game is on route!',
                #     'We hope you enjoy this game! we will be back to collect it on the pickup date!' ,
                #     'from@example.com',
                #     ['to@example.com'],
                #     fail_silently=False,
                # )

def getOnTimeJobsFromQuerySet(jobs):
    on_time_jobs_ids = set()
    for job in jobs:
        delivery_date = job.delivered_datetime
        due_date = job.due_delivery_datetime
        if due_date is not None and delivery_date is not None and due_date >= delivery_date:
            on_time_jobs_ids.add(job.id)
    return jobs.filter(pk__in=on_time_jobs_ids)


def getLateJobsFromQuerySet(jobs):
    late_jobs_ids = set()
    for job in jobs:
        delivery_date = job.delivered_datetime
        due_date = job.due_delivery_datetime
        if due_date is not None and delivery_date is not None and due_date < delivery_date:
            late_jobs_ids.add(job.id)
    return jobs.filter(pk__in=late_jobs_ids)


def getJobsByRegionAndPeriodPast(region, numdays):
    if region == None and numdays == None:
        return Job.objects.all()
    elif region == None:
        return Job.objects.filter(delivered_datetime__gte=(datetime.now() - timedelta(days=numdays)))
    elif numdays == None:
        return Job.objects.filter(county=region)
    else:
        return Job.objects.filter(delivered_datetime__gte=(datetime.now() - timedelta(days=numdays)),county=region)

def getJobsByRegionAndPeriodFuture(region, numdays):
    if region == None and numdays == None:
        return Job.objects.all()
    elif region == None:
        return Job.objects.filter(delivered_datetime__lte=(datetime.now() + timedelta(days=numdays)),delivered_datetime__gte=(datetime.now()))
    elif numdays == None:
        return Job.objects.filter(county=region)
    else:
        return Job.objects.filter(delivered_datetime__lte=(datetime.now() + timedelta(days=numdays)),delivered_datetime__gte=(datetime.now()), county=region)

def jobstats(request):
    # if POST request then the jobstats page is being filtered
    if request.method == 'POST':
        region = request.POST.get('region')
        days = request.POST.get('days')

        if region != 'All':
            if days == "1day":
                on_time_jobs = getOnTimeJobsFromQuerySet(getJobsByRegionAndPeriodPast(region,1)).order_by('-delivered_datetime')
                late_jobs = getLateJobsFromQuerySet(getJobsByRegionAndPeriodPast(region,1)).order_by('-delivered_datetime')
                undelivered_jobs = getJobsByRegionAndPeriodFuture(region,1).filter(delivered_datetime__isnull=True,job_list_id__isnull=False).order_by('-due_delivery_datetime')
                unallocated_jobs = getJobsByRegionAndPeriodFuture(region,1).filter(job_list_id__isnull = True).order_by('-due_delivery_datetime')
            elif days == "1 week":
                on_time_jobs = getOnTimeJobsFromQuerySet(getJobsByRegionAndPeriodPast(region, 7)).order_by('-delivered_datetime')
                late_jobs = getLateJobsFromQuerySet(getJobsByRegionAndPeriodPast(region, 7)).order_by('-delivered_datetime')
                undelivered_jobs = getJobsByRegionAndPeriodFuture(region, 7).filter(delivered_datetime__isnull=True,job_list_id__isnull=False).order_by('-due_delivery_datetime')
                unallocated_jobs = getJobsByRegionAndPeriodFuture(region, 7).filter(job_list_id__isnull=True).order_by('-due_delivery_datetime')
            elif days == "2 weeks":
                on_time_jobs = getOnTimeJobsFromQuerySet(getJobsByRegionAndPeriodPast(region, 14)).order_by('-delivered_datetime')
                late_jobs = getLateJobsFromQuerySet(getJobsByRegionAndPeriodPast(region, 14)).order_by('-delivered_datetime')
                undelivered_jobs = getJobsByRegionAndPeriodFuture(region, 14).filter(delivered_datetime__isnull=True,job_list_id__isnull=False).order_by('-due_delivery_datetime')
                unallocated_jobs = getJobsByRegionAndPeriodFuture(region, 14).filter(job_list_id__isnull=True).order_by('-due_delivery_datetime')
            elif days == "1 month":
                on_time_jobs = getOnTimeJobsFromQuerySet(getJobsByRegionAndPeriodPast(region, 30)).order_by('-delivered_datetime')
                late_jobs = getLateJobsFromQuerySet(getJobsByRegionAndPeriodPast(region, 30)).order_by('-delivered_datetime')
                undelivered_jobs = getJobsByRegionAndPeriodFuture(region, 30).filter(delivered_datetime__isnull=True,job_list_id__isnull=False).order_by('-due_delivery_datetime')
                unallocated_jobs = getJobsByRegionAndPeriodFuture(region, 30).filter(job_list_id__isnull=True).order_by('-due_delivery_datetime')
            else:
                on_time_jobs = getOnTimeJobsFromQuerySet(getJobsByRegionAndPeriodPast(region, None)).order_by('-delivered_datetime')
                late_jobs = getLateJobsFromQuerySet(getJobsByRegionAndPeriodPast(region, None)).order_by('-delivered_datetime')
                undelivered_jobs = getJobsByRegionAndPeriodFuture(region, None).filter(delivered_datetime__isnull=True).order_by('-due_delivery_datetime')
                unallocated_jobs = getJobsByRegionAndPeriodFuture(region, None).filter(job_list_id__isnull=True).order_by('-due_delivery_datetime')
        else:

            if days == "1day":
                on_time_jobs = getOnTimeJobsFromQuerySet(getJobsByRegionAndPeriodPast(None, 1)).order_by('-delivered_datetime')
                late_jobs = getLateJobsFromQuerySet(getJobsByRegionAndPeriodPast(None, 1)).order_by('-delivered_datetime')
                undelivered_jobs = getJobsByRegionAndPeriodFuture(None, 1).filter(delivered_datetime__isnull=True,job_list_id__isnull=False).order_by('-due_delivery_datetime')
                unallocated_jobs = getJobsByRegionAndPeriodFuture(None, 1).filter(job_list_id__isnull=True).order_by('-due_delivery_datetime')
            elif days == "1 week":
                on_time_jobs = getOnTimeJobsFromQuerySet(getJobsByRegionAndPeriodPast(None, 7)).order_by('-delivered_datetime')
                late_jobs = getLateJobsFromQuerySet(getJobsByRegionAndPeriodPast(None, 7)).order_by('-delivered_datetime')
                undelivered_jobs = getJobsByRegionAndPeriodFuture(None, 7).filter(delivered_datetime__isnull=True,job_list_id__isnull=False).order_by('-due_delivery_datetime')
                unallocated_jobs = getJobsByRegionAndPeriodFuture(None, 7).filter(job_list_id__isnull=True).order_by('-due_delivery_datetime')
            elif days == "2 weeks":
                on_time_jobs = getOnTimeJobsFromQuerySet(getJobsByRegionAndPeriodPast(None, 14)).order_by('-delivered_datetime')
                late_jobs = getLateJobsFromQuerySet(getJobsByRegionAndPeriodPast(None, 14)).order_by('-delivered_datetime')
                undelivered_jobs = getJobsByRegionAndPeriodFuture(None, 14).filter(delivered_datetime__isnull=True,job_list_id__isnull=False).order_by('-due_delivery_datetime')
                unallocated_jobs = getJobsByRegionAndPeriodFuture(None, 14).filter(job_list_id__isnull=True).order_by('-due_delivery_datetime')
            elif days == "1 month":
                on_time_jobs = getOnTimeJobsFromQuerySet(getJobsByRegionAndPeriodPast(None, 30)).order_by('-delivered_datetime')
                late_jobs = getLateJobsFromQuerySet(getJobsByRegionAndPeriodPast(None, 30)).order_by('-delivered_datetime')
                undelivered_jobs = getJobsByRegionAndPeriodFuture(None, 30).filter(delivered_datetime__isnull=True,job_list_id__isnull=False).order_by('-due_delivery_datetime')
                unallocated_jobs = getJobsByRegionAndPeriodFuture(None, 30).filter(job_list_id__isnull=True).order_by('-due_delivery_datetime')
            else:
                on_time_jobs = getOnTimeJobsFromQuerySet(getJobsByRegionAndPeriodPast(None, None)).order_by('-delivered_datetime')
                late_jobs = getLateJobsFromQuerySet(getJobsByRegionAndPeriodPast(None, None)).order_by('-delivered_datetime')
                undelivered_jobs = getJobsByRegionAndPeriodFuture(None, None).filter(delivered_datetime__isnull=True,job_list_id__isnull=False).order_by('-due_delivery_datetime')
                unallocated_jobs = getJobsByRegionAndPeriodFuture(None, None).filter(job_list_id__isnull=True).order_by('-due_delivery_datetime')

        on_time_jobs_count = on_time_jobs.count()
        late_jobs_count = late_jobs.count()
        undelivered_jobs_count = undelivered_jobs.count()
        unallocated_jobs_count = unallocated_jobs.count()

        context = {
            'searched_region': region,
            'day_sort': days,
            'on_time_jobs': on_time_jobs,
            'on_time_jobs_count': on_time_jobs_count,
            'late_jobs': late_jobs,
            'late_jobs_count': late_jobs_count,
            'undelivered_jobs': undelivered_jobs,
            'undelivered_jobs_count': undelivered_jobs_count,
            'unallocated_jobs': unallocated_jobs,
            'unallocated_jobs_count': unallocated_jobs_count
        }

    # if no POST request then show all job stats
    else:
        #Default to all regions, max time

        ############################### On Time Jobs vs Late Jobs ############################

        # On time jobs
        on_time_jobs = getOnTimeJobsFromQuerySet(getJobsByRegionAndPeriodPast(None, None)).order_by('-delivered_datetime')
        on_time_jobs_count = on_time_jobs.count()
        print("OnTime Jobs:", on_time_jobs_count)
        # Late jobs
        late_jobs = getLateJobsFromQuerySet(getJobsByRegionAndPeriodPast(None, None)).order_by('-delivered_datetime')
        late_jobs_count = late_jobs.count()
        print("Late Jobs:", late_jobs_count)

        ############################### Un-Delivered and Unallocated Jobs ############################

        # Un-Delivered jobs
        undelivered_jobs = Job.objects.filter(delivered_datetime__isnull=True,job_list_id__isnull = False).order_by('-due_delivery_datetime')
        undelivered_jobs_count = undelivered_jobs.count()
        print("Undelivered Jobs:", undelivered_jobs_count)
        # Unallocated jobs
        unallocated_jobs = Job.objects.filter(job_list_id__isnull = True).order_by('-due_delivery_datetime')
        unallocated_jobs_count = unallocated_jobs.count()
        print("Unallocated Jobs:",unallocated_jobs_count)

        context = {
            'searched_region': 'All',
            'day_sort': 'All time',
            'on_time_jobs': on_time_jobs,
            'on_time_jobs_count' : on_time_jobs_count,
            'late_jobs' : late_jobs,
            'late_jobs_count' : late_jobs_count,
            'undelivered_jobs' : undelivered_jobs,
            'undelivered_jobs_count' : undelivered_jobs_count,
            'unallocated_jobs' : unallocated_jobs,
            'unallocated_jobs_count' : unallocated_jobs_count
        }

    return render(request, 'jobstats.html', context)


def profile(request):
    current_user_id = request.user.id

    reviews = Reviews.objects.filter(left_by_user_id=current_user_id)
    context = {
        'reviews': reviews
    }
    return render(request, 'profile.html', context)


def account_settings(request):
    current_user_id = request.user.id
    # print(current_user_id)

    # reviews = Reviews.objects.filter(left_by_user_id = current_user_id)
    # context = {
    #     'reviews':reviews
    # }

    return render(request, 'rentalsystem/edit_account.html')


def account_details(request):
    controller = False
    current_user_id = request.user.id
    reviews = Reviews.objects.filter(left_by_user_id=current_user_id)
    if request.method == 'POST':
        usname = request.POST.get('username')
        email = request.POST.get('email')
        region = request.POST.get('region')
        card_number = request.POST.get('Card number')
        expiry_date = request.POST.get('Card expiry date')
        cvv = request.POST.get('Card cvv')
        user = User.objects.get(id=current_user_id)
        regions = [
            "Greater London",
            "West Midlands",
            "Greater Manchester",
            "West Yorkshire",
            "Hampshire",
            "Essex",
            "Kent",
            "Lancashire",
            "Merseyside",
            "South Yorkshire",
            "Devon",
            "Surrey",
            "Hertfordshire",
            "Noreth Yorkshire",
            "Nottinghamshire",
            "Tyne and Wear",
            "Staffordshire",
            "Lincolnshire",
            "Chesire",
            "Derbyshire",
            "Leicestershire",
            "Somerset",
            "Gloustershire",
            "Berkshire",
            "Norfolk",
            "Country Durham",
            "West Sussex",
            "Cambridgeshire",
            "East Sussex",
            "Buckinghamshire",
            "Dorset",
            "Suffolk",
            "Northamptonshire",
            "Wiltshire",
            "Oxfordshire",
            "Bedfordshire",
            "East Riding of Yorkshire",
            "Worcestershire",
            "Warwickshire",
            "Cornwall",
            "Cumbria",
            "Shropshire",
            "Bristol",
            "Northumberland",
            "Herefordshire",
            "Isle of Wight",
            "Rutland",
            "City of London",
        ]
        expiry = [
            'January',
            'February',
            'March',
            'April',
            'May',
            'June',
            'July',
            'August',
            'September',
            'October',
            'November',
            'December',
        ]
        error_selection = ["Username is already taken or you left it blank",
                           "Email is already taken or you left it blank",
                           "Region is invalid",
                           "Card number is invalid or you left it blank",
                           "Card expiry date is invalid or card has expired",
                           "Card CVV is invalid"]
        context = {
            'username': usname,
            'email': email,
            'region': region,
            'card_number': card_number,
            'expiry_date': expiry_date,
            'cvv' : cvv,
            'reviews': reviews,
            'controller': controller,
        }
        username_list = list(User.objects.values_list('username', flat=True))
        username_list.remove(user.username)
        if usname != '' and usname not in username_list:
            # print('___________________')
            # print(username)
            # print('___________________')
            if usname == user.username and email != '' and card_number != '' and expiry_date != '' and cvv != '':
                context['controller'] = True
            user.username = usname
            user.save()
        else:
            context['error'] = error_selection[0]
            context['error_set'] = True
            return render(request, 'rentalsystem/profile.html', context)
        email_list = list(User.objects.values_list('email', flat=True))
        email_list.remove(user.email)
        if email != '' and email not in email_list:
            # print('___________________')
            # print(email)
            # print('___________________')
            if email == user.email and usname != '' and card_number != '' and expiry_date != '' and cvv != '':
                context['controller'] = True
            user.email = email
            user.save()
        else:
            context['error'] = error_selection[1]
            context['error_set'] = True
            return render(request, 'rentalsystem/profile.html', context)
        if region in regions:
            # print('___________________')
            # print(region)
            # print('___________________')
            user.region = region
            user.save()
        else:
            context['error'] = error_selection[2]
            context['error_set'] = True
            return render(request, 'rentalsystem/profile.html', context)
        card_number_list = list(User.objects.values_list('card_long_number', flat=True))
        card_number_list.remove(user.card_long_number)
        if card_number != '' and card_number not in card_number_list:
            # print('___________________')
            # print(card_number)
            # print('___________________')
            if card_number == user.card_long_number and email != '' and usname != '' and expiry_date != '' and cvv != '':
                context['controller'] = True
            user.card_long_number = card_number
            user.save()
        else:
            context['error'] = error_selection[3]
            context['error_set'] = True
            return render(request, 'rentalsystem/profile.html', context)
        if expiry_date != '':
            # print('___________________')
            # print(expiry_date)
            # print('___________________')
            if expiry_date == user.card_expiry_date and email != '' and usname != '' and card_number != '' and cvv != '':
                context['controller'] = True
            user.card_expiry_date = expiry_date
            user.save()
        else:
            context['error'] = error_selection[4]
            context['error_set'] = True
            # print('___________________')
            # print(expiry_date)
            # print('___________________')
            return render(request, 'rentalsystem/profile.html', context)
        if cvv != '':
            # print('___________________')
            # print(cvv)
            # print('___________________')
            if cvv == user.card_cvv and email != '' and usname != '' and card_number != '' and expiry_date != '':
                context['controller'] = True
            user.card_cvv = cvv
            user.save()
        else:
            context['error'] = error_selection[5]
            context['error_set'] = True
            # print('___________________')
            # print(expiry_date)
            # print('___________________')
            return render(request, 'rentalsystem/profile.html', context)


    context['controller'] = True
    return render(request, 'rentalsystem/profile.html', context)


class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


def user_post_item(request):
    items = Item.objects.all()
    if request.method == 'POST':
        i_info = request.POST.get('i_info')
        i_cost = request.POST.get('i_cost')
        i_id = request.POST.get('i_id')
        context = {
            'items': items,
            'i_cost': i_cost,
            'info': i_info,
            'i_id': i_id
        }
    else:
        context = {
            'items': items,
        }
    return render(request, "user_post_item.html", context)


def post_item_details(request):
    if request.method == 'POST':
        i_id = request.POST.get('dropdown_value')  ##get the ID in dropdown
        print("=========", i_id)
        item = Item.objects.get(id=i_id)  ## gets the Item with that ID
        item_name = item.name  ##gets that Item's name
        info = request.POST.get('info_field')
        cost = request.POST.get('cost')
        context = {
            'item_name': item_name,
            'info': info,
            'cost': cost,
            'i_id': i_id
        }
    return render(request, 'rentalsystem/post_item_details.html', context)


def post_item_complete(request):
    if request.method == 'POST':
        i_id = Item.objects.get(id=request.POST.get('i_id'))#getting the item with that ID
        user_id = CustomUser.objects.get(id=request.user.id)
        ItemListing.objects.create(title=request.POST.get('i_name'),
                                   additional_info=request.POST.get('i_info'),
                                   cost_per_day=request.POST.get('i_cost'),
                                   owner_id=user_id,
                                   item_type_id=i_id)

    return render(request, 'rentalsystem/post_item_complete.html')


def leave_review(request):
    if request.method == 'POST':
        # get job id from the post request (button press)
        transactionpk = request.POST.get('transactionpk')
        transaction = Transaction.objects.filter(id=transactionpk).select_related('item_id').select_related(
            'owner_id').first()
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
        'review': Reviews.objects.filter(
            transaction_id=Transaction.objects.get(id=request.POST.get('transactionpk'))).last()
    }
    return render(request, 'rentalsystem/reviewconfirmation.html', context)


def my_orders(request):
    current_user_id = request.user.id

    # integration test - print current users id
    print("TEST: Current user ID is: " + str(current_user_id))

    # get all orders filtered to current user
    # use select_related to also query the item table (needed for item name)
    # filter by all orders with end date greater/equal(gte) than today
    current_orders = Transaction.objects.filter(renter_id=current_user_id, end_date__gte=
    datetime.now()).select_related('item_id').order_by('start_date')

    # get all orders filtered to current user
    # use select_related to also query the item table (needed for item name)
    # filter by all orders with end date less than(lt) than today
    completed_orders = Transaction.objects.filter(renter_id=current_user_id, end_date__lt=
    datetime.now()).select_related('item_id').prefetch_related('reviews_set').order_by('start_date')

    # integration test - print all orders
    print("TEST: Printing current users orders:")
    print(current_orders)

    context = {
        'current_orders': current_orders,
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

    itemcategorypairid = set()
    for itemcategorypair in ItemCategoryPair.objects.all():
        if itemcategorypair.item_id.id == item.id:
            itemcategorypairid.add(itemcategorypair.category_id.id)

    categories = Category.objects.filter(pk__in = itemcategorypairid)


    # save item into context so it's detailed can be rendered
    context = {
        'item': item,
        'categories' : categories
    }

    # will be POSTed if dates have been selected
    if request.method == 'POST':

        # get the start and end dates from the form
        s_date = request.POST.get('date_start')
        e_date = request.POST.get('date_end')

        print("Selecting items available between " + str(s_date) + " and " + str(e_date))
        print("HELLLLLOOOO")

        items = ItemListing.objects.filter(item_type_id=item.id)
        cost = 10

        # create context with all available item listings
        context = {
            'item': item,
            'item_listings': items,
            'dates': [s_date, e_date],
            'cost': cost,
            'categories' : categories
        }

        return render(request, "rentalsystem/itemListings.html", context)

    # if not POSTed then first time page has been loaded - no dates so
    # don't provide any items
    else:
        print('Not showing item listings yet: need dates')
        return render(request, "rentalsystem/itemListings.html", context)
