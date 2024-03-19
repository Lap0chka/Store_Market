from django.db import models
from django.urls import reverse
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200,unique=True)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name']), ]
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_product_count(self):
        return str(self.product.count())

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])


class SubCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name']), ]
        verbose_name = 'sub_category'
        verbose_name_plural = 'sub_categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])


class StarsRepresentationMixin:
    def stars_representation(self, rating):
        full_stars = int(rating)
        half_star = round(rating - full_stars, 1)

        stars_html = ''.join(
            f'<small class="fa fa-star text-primary mr-1"></small>'
            for _ in range(full_stars)
        )

        if half_star == 0.5:
            stars_html += '<small class="fa fa-star-half text-primary mr-1"></small>'
        elif half_star > 0.5:
            stars_html += '<small class="fa fa-star text-primary mr-1"></small>'

        return stars_html


class Product(models.Model, StarsRepresentationMixin):
    gender_choices = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
        ('U', 'Унисекс'),
    ]
    category = models.ForeignKey(Category, related_name='product', on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, related_name='product', null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    gender = models.CharField(max_length=1, choices=gender_choices, default='U')
    image = models.ImageField(upload_to='product/%Y/%m/%d',blank=True)
    color = models.CharField(max_length=50, default='black')
    description = models.TextField(blank=True)
    additional_information = models.TextField(blank=True)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.PositiveIntegerField(default=0)
    old_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)


    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])


    def save(self, *args, **kwargs):
        # Если скидка больше 0, обновляем поле price и устанавливаем old_price
        if self.discount > 0:
            discount_percentage = Decimal(self.discount) / Decimal(100)
            discounted_price = self.price - (self.price * discount_percentage)
            discounted_price = discounted_price.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
            self.old_price = self.price
            self.price = discounted_price
        self.color = self.color.title()
        super().save(*args, **kwargs)

    def average_rating(self):
        comments = self.comments.filter(active=True)  # Получаем только активные комментарии
        if comments.exists():
            total_rating = sum(comment.rating for comment in comments)
            return round(total_rating / comments.count(),2)
        else:
            return 5.0

    def stars_representation(self):
        return StarsRepresentationMixin.stars_representation(self, self.average_rating())


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_product_images')
    def upload_to(self, filename):
        # Генерация пути для загрузки изображения
        return f'products_image/{self.product.name}/{filename}'

    image = models.ImageField(upload_to=upload_to)

    def __str__(self):
        return f'Additional Image for {self.product.name}'


class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    size_name = models.CharField(max_length=50)
    # bust_size = models.PositiveIntegerField(null=True, blank=True)
    # waist_size = models.PositiveIntegerField(null=True, blank=True)
    # hip_size = models.PositiveIntegerField(null=True, blank=True)
    # width = models.PositiveIntegerField(null=True, blank=True)
    # height = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.size_name


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)

    def add_to_favorite(self, product):
        self.products.add(product)
        self.save()

    def remove_from_favorite(self, product):
        self.products.remove(product)

    def is_in_favorite(self, product):
        return self.products.filter(pk=product.pk).exists()



class Comment(models.Model, StarsRepresentationMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    rating = models.FloatField(default=0.0)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    dislikes = models.ManyToManyField(User, related_name='disliked_comments', blank=True)


    class Meta:
        ordering = ['created']
        indexes = [models.Index(fields=['created']), ]

    def __str__(self):
        return f'Comment by {self.user} on {self.product}'

    def stars_representation(self):
        return StarsRepresentationMixin.stars_representation(self, self.rating)

    def like(self, user):
        """
        Метод для установки лайка для комментария от указанного пользователя.
        """
        if user not in self.likes.all():
            self.likes.add(user)
            if user in self.dislikes.all():
                self.dislikes.remove(user)  # Если пользователь лайкает, удаляем дизлайк
            self.save()


    def dislike(self, user):
        """
        Метод для установки дизлайка для комментария от указанного пользователя.
        """
        if user not in self.dislikes.all():
            self.dislikes.add(user)
            if user in self.likes.all():
                self.likes.remove(user)  # Если пользователь дизлайкает, удаляем лайк
            self.save()


    def get_likes_count(self):
        """
        Метод для получения количества лайков комментария.
        """
        return self.likes.count()

    def get_dislikes_count(self):
        """
        Метод для получения количества дизлайков комментария.
        """
        return self.dislikes.count()

