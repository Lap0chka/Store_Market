from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, SubCategory, Product, Comment
from cart.forms import CartAddProductForm
from .recommender import Recommender
from random import sample
from django.db.models import Q, F
from .models import Favorite
from .forms import AddToFavoriteForm, CommentForm, ReplyCommentForm
from orders.models import OrderItem
from django.db.models import Count
from django.views.generic import TemplateView, ListView
from django.http import JsonResponse
from django.contrib import messages
from datetime import timedelta, datetime
from django.utils import timezone


class IndexView(TemplateView):
    template_name = 'shop/base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        all_products = Product.objects.filter(available=True)
        exclude_fields = []

        #Poplar products
        popular_products_items = OrderItem.objects.values('product').annotate(
            total_orders=Count('order', distinct=True)
        ).filter(product__available=True).order_by('-total_orders')[:8]
        popular_products_ids = popular_products_items.values_list('product', flat=True)
        popular_products = all_products.filter(id__in=popular_products_ids)
        all_products = all_products.exclude(Q(id__in=popular_products_ids))

        # Random Sale Products
        random_sale_products = all_products.filter(discount__gt=0).annotate(random_number=F('id') % 100).order_by(
            'random_number')[:4]
        exclude_fields.extend(random_sale_products.values_list('id', flat=True))
        random_sale_products_list = list(random_sale_products)
        random_sale_products_first, random_sale_products_second = random_sale_products_list[
                                                                  0:2], random_sale_products_list[2:4]

        # Random title products
        random_title_products = all_products.exclude(id__in=exclude_fields).order_by('?')[:3]
        random_title_products_list = list(random_title_products)
        exclude_fields.extend(random_title_products.values_list('id', flat=True))

        #  Recent products
        recent_products = list(all_products.exclude(
            id__in=exclude_fields).order_by(
            'created'))[:8]

        # Categories
        categories = sample(list(Category.objects.all()), 12)

        #Forms
        cart_product_form = CartAddProductForm(initial={'quantity': 1})
        form = AddToFavoriteForm()

        context['categories'] = categories
        context['random_sale_products_first'] = random_sale_products_first
        context['random_sale_products_second'] = random_sale_products_second
        context['title_products'] = random_title_products_list
        context['popular_products'] = popular_products
        context['recent_products'] = recent_products
        context['cart_product_form'] = cart_product_form
        context['form'] = form

        return context


    def post(self, request):
        form_type = request.POST.get('form_type', None)

        if form_type == 'heart':
            if request.user.is_authenticated:
                favorite, created = Favorite.objects.get_or_create(user=request.user)
                form = AddToFavoriteForm(request.POST)

                if form.is_valid():
                    product_id = form.cleaned_data['product_id']
                    product = Product.objects.get(id=product_id)
                    favorite.add_to_favorite(product)
            else:
                return redirect('user:login')

        return self.get(request)


class ProductsList(ListView):
    template_name = 'shop/product/list.html'
    model = Product
    paginate_by = 9
    context_object_name = 'products'

    def post(self, request):
        if request.user.is_authenticated:
            favorite, created = Favorite.objects.get_or_create(user=request.user)
            form = AddToFavoriteForm(request.POST)
            if form.is_valid():
                product_id = form.cleaned_data['product_id']
                product = Product.objects.get(id=product_id)
                favorite.add_to_favorite(product)
        else:
            return redirect('user:login')

        return self.get(request)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_product_form = CartAddProductForm(initial={'quantity': 1})
        color_counts = Product.objects.filter(available=True).values('color').annotate(count=Count('color'))
        color_counts_dict = {item['color'].title(): item['count'] for item in color_counts}
        context['categories'] = Category.objects.all()
        context['color_counts'] = color_counts_dict
        context['sub_categories'] = SubCategory.objects.all()
        context['form_favorite'] = AddToFavoriteForm()
        context['cart_product_form'] = cart_product_form
        return context

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        price_search = self.request.GET.getlist('price')
        products = Product.objects.filter(available=True)
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=category)
        if len(price_search) > 0:
            price_num = [int(num) for couple in price_search for num in couple.split()]
            min_price, max_price = min(price_num), max(price_num)
            products = products.filter(price__lte=max_price, price__gte=min_price)
        return products


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm()
    r = Recommender()
    recommended_products = r.suggest_products_for([product], 4)
    comments = product.comments.filter(active=True, parent=None)

    try:
        last_comment = Comment.objects.filter(user=request.user, product=product).latest('created').created
    except Comment.DoesNotExist:
        last_comment = timezone.make_aware(datetime(2024, 1, 1), timezone.utc)

    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        reply_form = ReplyCommentForm(data=request.POST)
        is_admin = request.user.is_staff
        rating = request.POST.get('rating')

        if form.is_valid() and (is_admin or last_comment + timedelta(weeks=1) < timezone.now()):
            if rating is None or not rating.isdigit():
                messages.error(request, 'Please choose a valid rating')
            else:
                comment = form.save(commit=False)
                comment.product = product
                comment.user = request.user
                comment.save()

                reply_form = ReplyCommentForm()
                form = CommentForm()
                messages.success(request, 'Comment successfully added!')

        elif reply_form.is_valid():
            parent_id = int(request.POST.get('parent_id'))
            parent_comment = Comment.objects.get(id=parent_id)
            reply = reply_form.save(commit=False)
            reply.parent = parent_comment  # Установите родительский комментарий
            reply.product = parent_comment.product  # Установите продукт, если необходимо
            reply.user = request.user
            reply.save()

            messages.success(request, 'Reply successfully added!')
            reply_form = ReplyCommentForm()
            form = CommentForm()
        else:
            messages.error(request, 'Sorry, there was an issue. Please try later.')

    else:
        form = CommentForm()
        reply_form = ReplyCommentForm()

    return render(request, 'shop/product/detail.html', {'product': product,

                                                        'cart_product_form': cart_product_form,
                                                        'recommended_products': recommended_products,
                                                        'comments': comments,
                                                        'form': form,
                                                        'reply_form': reply_form,
                                                        })


class ListFavorites(ListView):
    template_name = 'shop/product/favorite.html'
    model = Favorite
    context_object_name = 'favorite_products'

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_product_form = CartAddProductForm()
        context['cart_product_form'] = cart_product_form
        return context

    def post(self, request, *args, **kwargs):
        form = AddToFavoriteForm(request.POST)

        if form.is_valid():
            product_id = form.cleaned_data['product_id']
            product = Product.objects.get(id=product_id)
            favorite, created = Favorite.objects.get_or_create(user=request.user)
            favorite.remove_from_favorite(product)

        return redirect('shop:list_favorite')




