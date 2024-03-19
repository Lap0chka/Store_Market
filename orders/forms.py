from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control",
        'placeholder': "John"
    }))
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control",
        'placeholder': "Doe"
    }))
    email = forms.CharField(widget=forms.EmailInput(attrs={
        'class': "form-control py-4",
        'placeholder': "example@email.com"
    }))
    address = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control",
        'placeholder': "Georg-Lehnig-straße 1"
    }))
    postal_code = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control",
        'placeholder': "13253"
    }))
    city = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control",
        'placeholder': "Berlin"
    }))
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address',
        'postal_code', 'city']