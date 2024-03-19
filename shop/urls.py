from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('products/', views.ProductsList.as_view(), name='product_list'),
    path('products/<slug:category_slug>/', views.ProductsList.as_view(), name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('favorites/', views.ListFavorites.as_view(), name='list_favorite'),

]
