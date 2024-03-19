from django import forms


class CouponApplyForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': "form-control border-0 p-4",
        'placeholder': "Coupon Code"
    }))
