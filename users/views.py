from django.shortcuts import render
from django.views.generic import UpdateView
from django.contrib.auth.models import User
from .forms import UserProfileForm, OrderUpdateForm


class ProfileandAdressView(UpdateView):
    template_name = 'users/profile.html'
    form_class = UserProfileForm
    model = User

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(ProfileandAdressView, self).get_context_data(**kwargs)
        context['order_form'] = OrderUpdateForm()
        return context
