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
    list_display = ['name', 'info']
    fields = ('name', 'info')

    # inlines ability to change different model from this one
    inlines = [ItemCategoryPairInline]


#transaction view in admin page
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['item_id', 'owner_id', 'renter_id', 'total_cost','start_date','end_date']
    field = ('item_id', 'owner_id', 'renter_id', 'total_cost','start_date','end_date')


#joblistview in admin page
class JobListAdmin(admin.ModelAdmin):
    list_display = ['staff_id']
    field = ('staff_id')


class JobAdmin(admin.ModelAdmin):
    list_display = ['transaction_id','job_list_id','due_delivery_datetime','delivered_datetime']
    field = ('transaction_id','job_list_id','due_delivery_datetime','delivered_datetime')


# register the models with the admin site
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Item, ItemAdmin)
admin.site.register(models.Transaction, TransactionAdmin)
admin.site.register(models.JobList, JobListAdmin)
admin.site.register(models.Job, JobAdmin)
admin.site.register(Profile)

