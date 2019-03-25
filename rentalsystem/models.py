from django.db import models
from django.contrib.auth.models import AbstractUser

# subclassing django's default user class to make our own user class - AbstractUser superclass contains all the
# password and session magic we need
class CustomUser(AbstractUser):
    # tuple list stores the different roles a user can have
    ROLE_TYPES = (
        ('C', 'Customer'),
        ('S', 'Staff'),
        ('A', 'Admin'),
    )

    role = models.CharField(max_length=50, choices=ROLE_TYPES)  # stores customer/staff/admin role
    region = models.CharField(max_length=100)               # stores region
    name = models.CharField(max_length=100)                 # stores full name of user
    job_capacity = models.IntegerField(blank=True, null=True)          # STAFF ONLY: number of jobs they can do per day
    card_long_number = models.IntegerField(blank=True, null=True)      # CUSTOMER ONLY: payment card long number
    card_expiry_date = models.DateField(blank=True, null=True)         # CUSTOMER ONLY: payment card expiry date
    card_cvv = models.IntegerField(blank=True, null=True)              # CUSTOMER ONLY: payment card cvv code

    def __str__(self):
        return self.email


# category class
class Category(models.Model):
    title = models.CharField(max_length=100)                # holds the title of the category
    description = models.CharField(max_length=500)          # holds the description of the category


# item class
class Item(models.Model):
    name = models.CharField(max_length=100)                 # Name of generic item
    info = models.CharField(max_length=500, blank=True)     # description of item
    category_id = models.ForeignKey(Category, on_delete=models.PROTECT) # foreign key to Category


# item listing class
class ItemListing(models.Model):
    title = models.CharField(max_length=100)                    # Title for item listing
    additional_info = models.CharField(max_length=500, blank=True)     # optional description of item listed
    cost_per_day = models.PositiveIntegerField()            # holds the cost per day, must be positive
    owner_id = models.ForeignKey(CustomUser, on_delete=models.PROTECT)  # foreign key to CustomUser
    item_type_id = models.ForeignKey(Item, on_delete=models.PROTECT) # foreign key to Item


# transaction class
class Transaction(models.Model):
    item_id = models.ForeignKey(Item, on_delete=models.PROTECT) # foreign key to Item
    owner_id = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='owner_id')
    renter_id = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name ='renter_id')
    total_cost = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()


# job list class
class JobList(models.Model):
    staff_id = models.ForeignKey(CustomUser, on_delete=models.PROTECT)


# job class
class Job(models.Model):
    transaction_id = models.ForeignKey(Transaction, on_delete=models.PROTECT)
    job_list_id = models.ForeignKey(JobList, on_delete=models.PROTECT)
    delivered_datetime = models.DateTimeField(blank=True, null=True)


# dispute class
class Dispute(models.Model):
    transaction_id = models.ForeignKey(Transaction, on_delete=models.PROTECT)
    content = models.CharField(max_length=500, blank=True, null=True)
    resolved = models.BooleanField(default=False)


# payment class
class Payment(models.Model):
    transaction_id = models.ForeignKey(Transaction, on_delete=models.PROTECT)
    user_id = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    payment_amt = models.PositiveIntegerField()
    payment_date = models.DateTimeField()


# reviews class
class Reviews(models.Model):
    # review can be left for either a transaction or a customer? not sure what we wanna do here
    transaction_id = models.ForeignKey(Transaction, on_delete=models.PROTECT)
    content = models.CharField(max_length=500)
    rating = models.PositiveIntegerField()
    left_by_user = models.ForeignKey(CustomUser, on_delete=models.PROTECT)





