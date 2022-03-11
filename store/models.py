
from operator import truediv
from django.urls import reverse
from django.db import models
from category.models import Category
from accounts.models import Account


class Product(models.Model):
    product_name            = models.CharField(max_length=200, unique=True)
    slug                    = models.CharField(max_length=200, unique=True)
    description             = models.TextField(max_length=500, blank=True)
    price                   = models.IntegerField()
    stock                   = models.IntegerField()
    images                  = models.ImageField(upload_to='photos/products')
    is_available            = models.BooleanField(default=True)
    category                = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date            = models.DateTimeField(auto_now_add=True)
    modified_date           = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name

variation_category_choices = (
    ('color', 'color'),
    ('size', 'size'),
)

class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category = 'color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(variation_category = 'size', is_active=True)

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100, choices=variation_category_choices)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    creadted_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=100, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.subject