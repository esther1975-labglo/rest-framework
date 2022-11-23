from django.db import models
from django.contrib.auth.models import User
import uuid
import json
from django.db.models.lookups import IntegerFieldFloatRounding

Order_choices = [
    ('P', 'PENDING'),
    ('F', 'FAILED'),
    ('S', 'SUCCESS'),
]

Payment_choices = [
    ('P', 'PENDING'),
    ('F', 'FAILED'),
    ('S', 'SUCCESS'),
]

class TimeStampBaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  


class Brand(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="static/image/")
    
    def __str__(self):
        return self.title


class Review(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
    feedback = models.TextField(null = True)


class Product(TimeStampBaseModel):
    title = models.CharField(max_length = 50)
    name = models.CharField(max_length = 50)
    price = models.FloatField(default = 10.55)
    brand = models.ForeignKey(Brand, on_delete = models.CASCADE, blank = True, null = True)
    image = models.ImageField(upload_to = "static/image/")
    feedback = models.ForeignKey(Review, on_delete = models.CASCADE, blank = True, null = True)
    stock_aval = models.BooleanField(null = True)
        
    @staticmethod
    def autocomplete_search_fields():
        return ("title__icontains", "name__icontains", "price__icontains", "image__icontains")
    
    def __str__(self):
        return self.name

class Cart(TimeStampBaseModel):
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
    cart_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_active = models.BooleanField(default=False)
	

class Cartitems(TimeStampBaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product =  models.ForeignKey(Product, null = True, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    tax = models.FloatField(default=22.50)
    
        
class Order(TimeStampBaseModel):
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
    product =  models.ForeignKey(Product, null = True, on_delete=models.CASCADE)
    cart_items = models.ManyToManyField(Cartitems)
    status = models.BooleanField(default = False)


class ProductOrder(TimeStampBaseModel):
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
    cart_product = models.ManyToManyField(Cart)
    tax = models.FloatField()
    status = models.IntegerField(
        choices=Order_choices
    )

    def __str__(self):
        return self.user.username

class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE)
    address = models.CharField(max_length = 100)
    city = models.CharField(max_length = 100)
    state = models.CharField(max_length = 100)
    zipcode = models.CharField(max_length = 100)

    def __str__(self):
        return self.address


class Wishlist(TimeStampBaseModel):
	user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)
	wished_item = models.ForeignKey(Product, on_delete = models.CASCADE)
	added_date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.wished_item.title

class Payment(models.Model):
    transaction_id = models.TextField()
    order = models.ForeignKey(Cart, null = True, on_delete = models.CASCADE)
    status = models.CharField(max_length = 1, default = "P", null = True, choices = Payment_choices)




