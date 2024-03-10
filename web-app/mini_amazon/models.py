from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Users(User):
    def __str__(self):
        return self.username


class Upss(models.Model):
    ups_name = models.CharField(max_length=100, default=None)
    user = models.ForeignKey(to='Users',
                             on_delete=models.CASCADE,
                             blank=True, null=True)

class Address(models.Model):
    address_x = models.IntegerField(default=0)
    address_y = models.IntegerField(default=0)
    # whether this address is commonly used or not
    is_used = models.BooleanField(default=False)
    user = models.ForeignKey(to='Users',
                             on_delete=models.CASCADE,
                             blank=True, null=True)

# product categories
class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Products(models.Model):
    pdname = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    price = models.FloatField(default=0)
    # can be 5??????????
    avg_rating = models.FloatField(default=5)
    total_rating = models.FloatField(default=0)
    num_rating = models.IntegerField(default=0)
    # ??????????
    image = models.ImageField(upload_to='products', max_length=300, default="/static/images/products/sample.jpg")
    
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    def __str__(self):
        return self.pdname

class Packages(models.Model):
    STATUS_CHOICES = (
        (0, 'BUYING'),
        (1, 'BOUGHT'),
        (2, 'PACKING'),
        (3, 'PACKED'),
        (4, 'LOADING'),
        (5, 'LOADED'),
        (6, 'DELIVERING'),
        (7, 'DELIVERED'),
        (8, 'DELETE'),
    )
    create_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(to=Users, on_delete=models.CASCADE, blank=True, null=True)
    product_id = models.ForeignKey(to=Products, on_delete=models.CASCADE, blank=True, null=True)
    purchase_quantity = models.IntegerField(default=0)
    # status > buying
    # change to ups_name??????????????
    ups_name = models.ForeignKey(
        to="Upss", on_delete=models.CASCADE, blank=True, null=True)
    dest_address = models.ForeignKey(to=Address, on_delete=models.CASCADE, blank=True, null=True)
    # product price when product is bought
    bought_price = models.IntegerField(default=0, blank=True, null=True)
    # status=delivered
    rating = models.FloatField(default=0)
    truck_id = models.IntegerField(null=True,blank=True)
    # ForeignKey Warehouse?????????????????????
    warehouse_id = models.IntegerField(default=0, blank=True, null=True)
    status = models.IntegerField(
        choices=STATUS_CHOICES, default=0, blank=True, null=True)
    is_processing = models.BooleanField(default=False)

class Warehouse(models.Model):
    x = models.IntegerField()
    y = models.IntegerField()


class Inventories(models.Model):
    warehouse_id = models.IntegerField(default=0, blank=True, null=True)
    product_id = models.IntegerField(default=0, blank=True, null=True)
    inventory_quantity = models.IntegerField(default=0)


class Emails(models.Model):
    user_id = models.IntegerField(default=0, blank=True, null=True)
    email_address = models.CharField(max_length=200)

class Subscriber(models.Model):
    email_address = models.CharField(max_length=200)