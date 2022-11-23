from django.contrib import admin
from store.models import (
    Product,
    Brand,
    Cart,
    Cartitems,
    Order,
    ProductOrder,
    ShippingAddress,
    Wishlist,
    Payment,
    Review
)
    
admin.site.register(Product)
admin.site.register(Brand)
admin.site.register(Cart)
admin.site.register(Cartitems)
admin.site.register(Order)
admin.site.register(ProductOrder)
admin.site.register(Wishlist)
admin.site.register(ShippingAddress)
admin.site.register(Payment)
admin.site.register(Review)



