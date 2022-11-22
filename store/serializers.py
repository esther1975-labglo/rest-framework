from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
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
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        token = serializers.SerializerMethodField('get_user_token')

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'])

        return user

    def get_user_token(self, obj):
        return Token.objects.get_or_create(user=obj)[0].key

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        label = "Username",
        write_only = True
    )
    password = serializers.CharField(
        label = "Password",
        style = {'input_type': 'password'},
        trim_whitespace = False,
        write_only = True
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request = self.context.get('request'),
                                username = username, password = password)
            if not user:
                msg = 'Access denied: wrong username or password.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Both "username" and "password" are required.'
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('title', 'image')

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = ('url', 'title', 'name', 'price', 'brand', 'image', 'feedback', 'stock_aval')

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ('user', 'cart_id', 'is_active')

class CartitemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cartitems
        fields = ('cart', 'product', 'quantity', 'tax')

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('user', 'product', 'cart_items', 'status')

class ProductOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductOrder
        fields = ('user', 'cart_product', 'tax', 'status') 

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ('user', 'cart', 'address', 'city', 'state', 'zipcode')               

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ('user', 'wished_item', 'added_date')

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('transaction_id', 'order', 'status')

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('user', 'feedback')