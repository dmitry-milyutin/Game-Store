from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistrationForm(UserCreationForm):
    usable_password = None
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]