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
    RegisterSerializer,
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

'''user registeration'''

class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token,created=Token.objects.get_or_create(user=user)
        return Response({
        "token": token.key,    
        "user": UserSerializer(user, context=self.get_serializer_context()).data,
        }, status=status.HTTP_200_OK)


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
    serializer_class = CartSerializer
    queryset = Cart.objects.all()


class CartitemsViewSet(viewsets.ModelViewSet):
    serializer_class = CartitemsSerializer
    queryset = Cartitems.objects.all()


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()


class ProductOrderViewSet(viewsets.ModelViewSet):
    serializer_class = ProductOrderSerializer
    queryset = ProductOrder.objects.all()


class ShippingAddressViewSet(viewsets.ModelViewSet):
    serializer_class = ShippingAddressSerializer
    queryset = ShippingAddress.objects.all()


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    queryset = Wishlist.objects.all()


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()


@api_view(['POST'])
def test_payment(request):
    test_payment_intent = stripe.PaymentIntent.create(
    amount=1000, currency='pln', 
    payment_method_types=['card'],
    receipt_email='test@example.com')
    return Response(status = status.HTTP_200_OK, data = test_payment_intent) 


stripe.api_key = settings.SECRET_KEY


class CheckoutSessionCreateAPIView(View):
    def post(self, request, *args, **kwargs):
        product_id = Product.objects.get(id = 1)
        product = Product.objects.get(name=product_id)
        YOUR_DOMAIN = "http://127.0.0.1:8000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount':int(product.price)
                        ,
                        'product_data': {
                            'name': product.name,
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "product_id": product.id
            },
            mode='payment',
            #success_url = YOUR_DOMAIN + '/success/',
            #cancel_url = YOUR_DOMAIN + '/cancel/',
        )
        
        print("checkout_session", checkout_session)
        #event = json.loads(checkout_session)
        #print("HELLO", event)
        #if event['type'] == 'checkout.session.completed':
            #session = event['data']['object']
            #sessionID = session['id']
            #ID = session['metadata']['product_id']
            #Payment.objects.filter(id = ID).update(paid = True, description = sessionID)
        return redirect(checkout_session.url, status=200)


class StripeCheckoutSessionCreateAPIView(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=self.kwargs.get('order_id'))
        order_items = []
        for order_item in order.objects.all():
            product = order_item.product
            quantity = order_item.quantity
            data = {
                'price_data': {
                    'currency': 'usd',
                    'unit_amount_decimal': product.price,
                    'product_data': {
                        'name': product.name,
                    }
                },
        
            }

            order_items.append(data)

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=order_items,
            metadata={
                "order_id": order.id
            },
            mode='payment',
            #success_url=settings.PAYMENT_SUCCESS_URL,
            #cancel_url=settings.PAYMENT_CANCEL_URL
        )

        return Response({'sessionId': checkout_session['id']}, status=status.HTTP_201_CREATED)


class StripeWebhookAPIView(APIView):
    def post(self, request, format=None):
        payload = request.body
        endpoint_secret = settings.WEBHOOK_KEY
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret)
        except ValueError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            customer_email = session['customer_details']['email']
            order_id = session['metadata']['order_id']

            print('Payment successfull')

            payment = get_object_or_404(Payment, order=order_id)
            payment.status = 'S'
            payment.save()

            order = get_object_or_404(Order, id=order_id)
            order.status = 'S'
            order.save()

            send_payment_success_email_task.delay(customer_email)
        return Response(status=status.HTTP_200_OK)