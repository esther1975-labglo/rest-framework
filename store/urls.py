from django.urls import path, include
from rest_framework.routers import DefaultRouter
from store import views
from .views import (

    UserViewSet,
    ProductViewSet,
    BrandViewSet,
    CartViewSet,
    CartitemsViewSet,
    OrderViewSet,
    ProductOrderViewSet,
    ShippingAddressViewSet,
    WishlistViewSet,
    PaymentViewSet,
    LoginView,
    ReviewViewSet,
    StripeCheckoutSessionCreateAPIView,
    StripeWebhookAPIView

)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'products', ProductViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'carts', CartViewSet)
router.register(r'cartitems', CartitemsViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'productorders', ProductOrderViewSet)
router.register(r'shipping_address', ShippingAddressViewSet)
router.register(r'wishlist', WishlistViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view()),
    path('stripe_payment', views.test_payment, name = 'payment'),
    path('stripe_create-checkout-session',StripeCheckoutSessionCreateAPIView.as_view(), name='checkout_session'),
    path('stripe/webhook/', StripeWebhookAPIView.as_view(), name='stripe_webhook'),
]