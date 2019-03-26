from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from .models import Category

# a form which extends the built-in Django UserCreationForm - required because we're overriding the built in User, so
# we need to define a new Meta class to tell it to use the CustomUser model
class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email')

# a form which extends the built-in Django UserChangeForm - required because we're overriding the built in User, so
# we need to define a new Meta class to tell it to use the CustomUser model
class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email')


# used to add categories in the add_category.html template
class AddCategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'description']
