from Cart.models import Order, OrderItem, TransferNotification
from django.db.models import fields
from Store.models import BookBank, Product, ProductImages, SocialQRCode, Store, StoreLocation
from rest_framework import serializers
from django.contrib.auth.models import User, Group


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'first_name', 'last_name', 'email']


class MyUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'first_name', 'last_name', 'email']


class UserRegisSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def save(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )

        user.set_password(validated_data['password'])
        user.save()
        return user


class StoreSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()

    class Meta:
        model = Store
        fields = '__all__'


class BookBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookBank
        fields = '__all__'


class ProductProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class OrderProfileSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField()
    receive_address = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = '__all__'


class OrderItemProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class BookBankObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookBank
        fields = '__all__'


class TransferNotificationSerializer(serializers.ModelSerializer):
    bookbank = serializers.StringRelatedField()

    class Meta:
        model = TransferNotification
        fields = '__all__'


class SocialQRCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialQRCode
        fields = '__all__'


class StoreRegisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['name', 'slogan', 'about',
                  'phone1', 'phone2', 'district', 'status']

    def create(self, user, validated_data):
        data = {}
        data['owner'] = user
        for key in validated_data:
            if key in self.fields:
                data[key] = validated_data[key]

        return Store.objects.create(**data)

    def update(self, store, validated_data):
        data = {}
        for key in validated_data:
            if key in self.fields:
                data[key] = validated_data[key]

        return store.update(**data)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['grade', 'gene', 'values',
                  'price', 'weight', 'desc', 'status']

    def create(self, store_obj, validated_data):
        return Product.objects.create(
            store=store_obj,
            grade=validated_data['grade'],
            gene=validated_data['gene'],
            values=validated_data['values'],
            price=validated_data['price'],
            weight=validated_data['weight'],
            desc=validated_data['desc'],
            status=validated_data['status'],
        )

    def update(self, instance, validated_data):
        data = {}
        for key in validated_data:
            if key in self.fields:
                data[key] = validated_data[key]

        return instance.update(**data)


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = "__all__"


class BookBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookBank
        fields = ['store', 'bank', 'bank_branch',
                  'account_type', 'account_name', 'account_number']

    def create(self, store_obj, validated_data):
        return BookBank.objects.create(
            store=store_obj,
            bank=validated_data['bank'],
            bank_branch=validated_data['bank_branch'],
            account_type=validated_data['account_type'],
            account_name=validated_data['account_name'],
            account_number=validated_data['account_number']
        )

    def update(self, instance, validated_data):
        data = {}
        for key in validated_data:
            if key in validated_data:
                data[key] = validated_data[key]

        return instance.update(**data)


class StoreLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreLocation
        fields = ['store', 'latitude', 'longitude']

    def create(self, store_obj, validated_data):
        return StoreLocation.objects.create(
            store=store_obj,
            latitude=validated_data['latitude'],
            longitude=validated_data['longitude'],
        )

    def update(self, instance, validated_data):
        data = {}
        for key in validated_data:
            if key in validated_data:
                data[key] = validated_data[key]

        return instance.update(**data)
