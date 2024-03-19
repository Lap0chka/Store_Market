from django.contrib.auth.forms import UserChangeForm
from django import forms
from django.contrib.auth.models import User
from orders.models import Order


class UserProfileForm(UserChangeForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control py-2",
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control py-2",
    }))

    email = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control", 'readonly': True
    }))
    new_email = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control",
    }), required=False)
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': "form-control py-4",
        'placeholder': "Old Password"
    }), required=False)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': "form-control py-4",
        'placeholder': "New password"
    }), required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': "form-control py-4",
        'placeholder': "Confirm password"
    }), required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',
                  'new_email', 'old_password', 'password1', 'password2')


class OrderUpdateForm(UserChangeForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control",
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control",
    }))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': "form-control",
    }))
    address = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control",

    }))
    postal_code = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control",
    }))
    city = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control",
    }))

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address',
        'postal_code', 'city']