from django.db import models
from django.contrib.auth.models import AbstractUser

# subclassing django's default user class to make our own user class
class CustomUser(AbstractUser):
    # add additional fields in here

    def __str__(self):
        return self.email