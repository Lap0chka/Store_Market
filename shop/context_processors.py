from .models import Favorite, Comment, Product
from django.db.models import Avg


def favorite_items(request):
    if request.user.is_authenticated:
        favorite = Favorite.objects.get_or_create(user=request.user)[0]
        total_favorite_items = favorite.products.count()
    else:
        total_favorite_items = 0
    return {'total_favorite_items': total_favorite_items}


def len_all_products(request):
    len_products = len(Product.objects.filter(available=True))
    return {'len_all_products': len_products}

