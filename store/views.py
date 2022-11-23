from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from store.models import (
    User,
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
from store.serializers import (
    LoginSerializer,
    UserSerializer,
    ProductSerializer,
    BrandSerializer,
    CartSerializer,
    CartitemsSerializer,
    OrderSerializer,
    ProductOrderSerializer,
    ShippingAddressSerializer,
    WishlistSerializer,
    PaymentSerializer,
    ReviewSerializer
   
)
from rest_framework import permissions
from rest_framework import generics
from django.db.models import Q
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework import views
from django.contrib.auth import login
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from rest_framework import permissions
from django.conf import settings
import stripe
from django.shortcuts import render,redirect
import json
'''user login'''

class LoginView(views.APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (TokenAuthentication,)         

    def post(self, request, format=None):
        serializer = LoginSerializer(data=self.request.data)     
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(None, status=status.HTTP_200_OK)


'''user CRUD operation'''

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class BrandViewSet(viewsets.ModelViewSet):
    serializer_class = BrandSerializer
    queryset = Brand.objects.all()


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class CartViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CartSerializer
    queryset = Cart.objects.all()


class CartitemsViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CartitemsSerializer
    queryset = Cartitems.objects.all()


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OrderSerializer
    queryset = Order.objects.all()


class ProductOrderViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ProductOrderSerializer
    queryset = ProductOrder.objects.all()


class ShippingAddressViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ShippingAddressSerializer
    queryset = ShippingAddress.objects.all()


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    queryset = Wishlist.objects.all()


class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()


@api_view(['POST'])
def test_payment(request):
    permission_classes = (permissions.IsAuthenticated,)
    test_payment_intent = stripe.PaymentIntent.create(
    amount=1000, currency='pln', 
    payment_method_types=['card'],
    receipt_email='test@example.com')             
    print(test_payment_intent)
    return Response(status = status.HTTP_200_OK, data = test_payment_intent)                   

stripe.api_key = settings.SECRET_KEY

'''class StripeCheckoutSessionCreateAPIView(APIView):
    query_set = Payment
    def get(self, request):
        items = Payment.objects.all()
        serializer = PaymentSerializer(items, many=True)
        return Response(serializer.data)
    def post(self, request, format=None):
        order = Order.objects.all()
        domain_url = 'http://localhost:8000/'
        checkout_session = stripe.checkout.Session.create(
            client_reference_id=request.user.id if request.user.is_authenticated else None,
            success_url=domain_url +'success/',
            cancel_url=domain_url + 'cancelled/',
            payment_method_types=['card'],
            line_items=[
                    {
                        'price_data': {
                            'unit_amount': int(18000),
                            'currency': 'usd',
                            'product_data': {'name': 'vivo'},         
                        },
                        'quantity': 1,
                    }
                ],
            metadata={
                "order_id": order
            },
            mode='payment',
        )
        print(checkout_session)
        return redirect(checkout_session.url, status=status.HTTP_201_CREATED)


class WebhookView(APIView):
    def post(self, request, format=None):
        payload = request.body.decode('utf-8')
        print("payload", payload)
        event = json.loads(payload)
        print("HELLO", event)
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            sessionID = session['id']
            ID = session['metadata']['order_id']
            Payment.objects.create( transaction_id = session["id"],  status = 'P')
           # Payment.objects.filter(transaction_id = sessionID).update(status = True, description = sessionID)

        elif event['type'] == 'payment_intent.payment_failed':
            session = event['data']['object']
            sessionID = session['id']
            ID = session['metadata']['order']
           # Payment.objects.filter( transaction_id = sessionID).update(status = True, description = sessionID)
            Payment.objects.create( transaction_id = session['id'],  status = 'P')
        return Response(True, status=status.HTTP_200_OK)'''


class CheckoutSession(APIView):
    query_set = Payment
    def post(self, request, format=None):
        domain_url = 'http://localhost:8000/'      
        
        cart_product = Cart.objects.filter(
                Q(user_id= 1) & Q(is_active=True))
        
        order = Order.objects.create(status = True, user_id = User.objects.get(id = 1).id)
                                                                          
        checkout_session = stripe.checkout.Session.create(
            client_reference_id = request.user.id if request.user.is_authenticated else None,
            success_url = domain_url,
            cancel_url = domain_url,
            payment_method_types=['card'],
            line_items=[
                    {
                        'price_data': {
                            'unit_amount': int(18000),
                            'currency': 'usd',
                            'product_data': {'name': 'vivo'},
                        },
                        'quantity': 1,
                    }
                ],
            metadata = {
                "order_id": order.id
                },
            mode='payment',
        )
        print(checkout_session)
        return Response(checkout_session.url, status=status.HTTP_200_OK)
    
    
class Webhook(APIView):
    def post(self, request, format=None):
        payload = request.body.decode('utf-8')
        endpoint_secret = settings.SECRET_KEY 
        event = json.loads(payload)
        
        
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            transaction_id = session['id']
            print(transaction_id)
            order_id = event['data']['object']["metadata"]["order_id"]
            amount = event['data']['object']
            order = Order.objects.filter(id = order_id).update(status = True)
            Cart.objects.filter(user = 1).update(is_active = False)
            Payment.objects.create(transactionid = transaction_id, order = Order.objects.get(id = order_id))
        
        elif  event['type'] == "payment_intent.payment_failed":
            session = event['data']['object']
            transaction_id = session['id']
            amount = event['data']['object']

        return Response(status=status.HTTP_200_OK)


