from django.contrib import admin
from rentalsystem import models
from django.contrib.auth.admin import UserAdmin


from rentalsystem.models import Job
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, ItemCategoryPair, Profile, JobList


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username', 'role', 'region', 'name', 'job_capacity',
                    'card_long_number', 'card_expiry_date', 'card_cvv']
    fieldsets = (
        ('Basic information', {
            'fields': ('email', 'username', 'role', 'region', 'name')
        }),
        ('Customer payment information', {
            'fields': ('card_long_number', 'card_expiry_date', 'card_cvv')
        }),
        ('Staff information', {
            'fields': ('job_capacity',)
        }),
    )


# sets up the category view in the admin page
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']
    fields = ('title', 'description')


# sets up the inline admin edit for ItemCategoryPair 
class ItemCategoryPairInline(admin.StackedInline):
    model = ItemCategoryPair
    list_display = ['']


# sets up the item view in the admin page
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'info', 'image']
    fields = ('name', 'info', 'image')

    # inlines ability to change different model from this one
    inlines = [ItemCategoryPairInline]


class ItemListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'additional_info', 'cost_per_day', 'owner_id', 'item_type_id']
    fields = ('title', 'additional_info', 'cost_per_day', 'owner_id', 'item_type_id')


# transaction view in admin page
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['item_id', 'owner_id', 'renter_id', 'total_cost','start_date','end_date']
    field = ('item_id', 'owner_id', 'renter_id', 'total_cost','start_date','end_date')


# joblistview in admin page
class JobListAdmin(admin.ModelAdmin):
    list_display = ['staff_id']
    field = ('staff_id')


class JobAdmin(admin.ModelAdmin):
    list_display = ['transaction_id','job_list_id','due_delivery_datetime','delivered_datetime']
    field = ('transaction_id','job_list_id','due_delivery_datetime','delivered_datetime')

    # def staff_name(self, obj):
    #     return obj.job_list_id

class ReviewAdmin(admin.ModelAdmin):
    list_display = ['transaction_id','content','item_rating','transaction_rating', 'left_by_user_id']
    field = ('transaction_id','content','item_rating','transaction_rating', 'left_by_user_id')


class AddressAdmin(admin.ModelAdmin):
    list_display = ['address1', 'address2', 'address3', 'address4', 'address5', 'post_code']
    field = ('address1', 'address2', 'address3', 'address4', 'address5', 'post_code')


# register the models with the admin site
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Item, ItemAdmin)
admin.site.register(models.Transaction, TransactionAdmin)
admin.site.register(models.JobList, JobListAdmin)
admin.site.register(models.Job, JobAdmin)
admin.site.register(Profile)
admin.site.register(models.ItemListing, ItemListingAdmin)
admin.site.register(models.Reviews, ReviewAdmin)
admin.site.register(models.Address, AddressAdmin)
