from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django import forms


# a form which extends the built-in Django UserCreationForm - required because we're overriding the built in User, so
# we need to define a new Meta class to tell it to use the CustomUser model
class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email', 'region', 'name')


# a form which extends the built-in Django UserChangeForm - required because we're overriding the built in User, so
# we need to define a new Meta class to tell it to use the CustomUser model
class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class DateForm(forms.Form):
    date = forms.DateTimeField(input_formats=['%Y/%m/%d %H:%M'])

