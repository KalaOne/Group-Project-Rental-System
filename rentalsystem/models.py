from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator

# subclassing django's default user class to make our own user class - AbstractUser superclass contains all the
# password and session magic we need
class CustomUser(AbstractUser):
    # tuple list stores the different roles a user can have
    ROLE_TYPES = (
        ('C', 'Customer'),
        ('S', 'Staff'),
        ('A', 'Admin'),
    )

    role = models.CharField(max_length=50, choices=ROLE_TYPES, default='C')  # stores customer/staff/admin role
    region = models.CharField(max_length=100)               # stores region
    name = models.CharField(max_length=100)                 # stores full name of user
    job_capacity = models.IntegerField(blank=True, null=True)          # STAFF ONLY: number of jobs they can do per day
    card_long_number = models.BigIntegerField(blank=True, null=True)      # CUSTOMER ONLY: payment card long number
    card_expiry_date = models.DateField(blank=True, null=True)         # CUSTOMER ONLY: payment card expiry date
    card_cvv = models.IntegerField(blank=True, null=True)              # CUSTOMER ONLY: payment card cvv code

    def __str__(self):
        return self.email

# stores addresses for customers
class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, db_column='CustomUser_id')
    address1 = models.CharField(max_length=200, blank=True, null=True)
    address2 = models.CharField(max_length=200, blank=True, null=True)
    address3 = models.CharField(max_length=200, blank=True, null=True)
    address4 = models.CharField(max_length=200, blank=True, null=True)
    address5 = models.CharField(max_length=200, blank=True, null=True)
    county = models.CharField(max_length=100)
    post_code = models.CharField(max_length=20, blank=True, null=True)

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.name} Profile'

# category class
class Category(models.Model):
    title = models.CharField(max_length=100)                # holds the title of the category
    description = models.CharField(max_length=500)          # holds the description of the category

    def __str__(self):
        return self.title


# item class
class Item(models.Model):
    name = models.CharField(max_length=100)                 # Name of generic item
    info = models.CharField(max_length=500, blank=True)     # description of item
    image = models.ImageField(default='default.jpg', upload_to='item_pics')

    def get_absolute_url(self):
        return reverse('post_item_details', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name


# Item category link, item can have multiple category pairs
class ItemCategoryPair(models.Model):
    item_id = models.ForeignKey(Item, on_delete=models.PROTECT, db_column='item_id')  # foreign key to Category
    category_id = models.ForeignKey(Category, on_delete=models.PROTECT, db_column='category_id')  # foreign key to Category


# item listing class
class ItemListing(models.Model):
    title = models.CharField(max_length=100)                    # Title for item listing
    additional_info = models.CharField(max_length=500, blank=True)     # optional description of item listed
    cost_per_day = models.PositiveIntegerField()            # holds the cost per day, must be positive
    owner_id = models.ForeignKey(CustomUser, on_delete=models.PROTECT, db_column='owner_id')  # foreign key to CustomUser
    item_type_id = models.ForeignKey(Item, on_delete=models.PROTECT, db_column='item_type_id') # foreign key to Item

    def __str__(self):
        return self.title

# transaction class
class Transaction(models.Model):
    item_id = models.ForeignKey(Item, on_delete=models.PROTECT, db_column='item_id') # foreign key to Item
    owner_id = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='owner_id')
    renter_id = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name ='renter_id')
    total_cost = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()


# job list class
class JobList(models.Model):
    staff_id = models.ForeignKey(CustomUser, on_delete=models.PROTECT, db_column='staff_id')


# job class
class Job(models.Model):
    transaction_id = models.ForeignKey(Transaction, on_delete=models.PROTECT, db_column='transaction_id')
    job_list_id = models.ForeignKey(JobList, on_delete=models.PROTECT, db_column='job_list_id', blank=True, null=True)
    due_delivery_datetime = models.DateTimeField()
    delivered_datetime = models.DateTimeField(blank=True, null=True)

    address1 = models.CharField(max_length=200, blank=True, null=True)
    address2 = models.CharField(max_length=200, blank=True, null=True)
    address3 = models.CharField(max_length=200, blank=True, null=True)
    address4 = models.CharField(max_length=200, blank=True, null=True)
    address5 = models.CharField(max_length=200, blank=True, null=True)
    county = models.CharField(max_length=100)
    post_code = models.CharField(max_length=20, blank=True, null=True)


# dispute class
class Dispute(models.Model):
    transaction_id = models.ForeignKey(Transaction, on_delete=models.PROTECT, db_column='transaction_id')
    content = models.CharField(max_length=500, blank=True, null=True)
    resolved = models.BooleanField(default=False)


# payment class
class Payment(models.Model):
    transaction_id = models.ForeignKey(Transaction, on_delete=models.PROTECT, db_column='transaction_id')
    user_id = models.ForeignKey(CustomUser, on_delete=models.PROTECT, db_column='user_id')
    payment_amt = models.PositiveIntegerField()
    payment_date = models.DateTimeField()


# reviews class
class Reviews(models.Model):
    # review can be left for either a transaction or a customer? not sure what we wanna do here
    transaction_id = models.ForeignKey(Transaction, on_delete=models.PROTECT, db_column='transaction_id')
    content = models.CharField(max_length=500)
    item_rating = models.PositiveIntegerField(
        default = 3,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ])
    transaction_rating = models.PositiveIntegerField(
        default = 3,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ])
    left_by_user_id = models.ForeignKey(CustomUser, on_delete=models.PROTECT, db_column='left_by_user_id')





