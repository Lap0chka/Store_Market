from django import forms
from .models import Product, Comment


class AddToFavoriteForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput(attrs={'class': 'form-control'}))


class CommentForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(attrs={
        'class': "form-control form-control-lg",
        'placeholder': "Add comment",

    }))
    rating = forms.IntegerField(
        widget=forms.NumberInput(attrs={'type': 'number', 'min': 1, 'max': 5, 'class': 'form-control'}),
        label='Rating',
    )

    class Meta:
        model = Comment
        fields = ['body', 'rating']


class ReplyCommentForm(forms.ModelForm):
    body = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 3,
        'placeholder': 'Reply to the comment',
    }), required=False)

    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'parent': forms.HiddenInput(),
        }