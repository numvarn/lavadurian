from Cart.views import BOX_SIZE_1_PRICE, BOX_SIZE_2_PRICE, orderBoxCalculate, shippingCostCalculate
import requests
from decimal import Decimal
from uuid import uuid4
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import generics
from rest_framework import filters
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework.serializers import Serializer
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
from rest_framework import pagination
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from django.db.models import Count

import json
from DurianAPI import serializers
from Members.models import Trader
from Store.models import BookBank, Product, ProductImages, SocialQRCode, Store, StoreLocation
from Store.models import DISTRICT_CHOICES, STATUS_CHOICES, SOCIAL_TYPE
from Store.views import getModelChoice
from Cart.models import Order, OrderItem, TransferNotification

# Create your views here.
'''
Get all user list
'''


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]


'''
Get all Store list
'''


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all().order_by('-date_created')
    serializer_class = serializers.StoreAllSerializer
    permission_classes = [permissions.AllowAny]
    pagination.PageNumberPagination.page_size = 500


'''
Get current user that loged-in to system
'''


@permission_classes((IsAuthenticated,))
class GetMyUserViewSet(generics.ListAPIView):
    serializer_class = serializers.MyUserSerializer

    def get_queryset(self):
        user_id = self.request.user.id
        return User.objects.filter(id=user_id)


'''
For Regist new user to system
'''


@csrf_exempt
@api_view(["GET", ])
@permission_classes((IsAuthenticated,))
def GetStoreProfileAPI(request):
    profile = {}
    store_lt = []
    product_lt = []
    order_lt = []
    orderItem_lt = []
    images_lt = []
    bookbank_lt = []
    qrcode_lt = []
    status_lt = []
    location_lt = []

    status_msg = HTTP_403_FORBIDDEN

    status = False
    msg = "access stores and product"
    stores = Store.objects.filter(owner=request.user)
    for store in stores:
        store_lt.append(serializers.StoreSerializer(store).data)

        bookbank_qs = BookBank.objects.filter(store=store)
        for bookbank in bookbank_qs:
            bookbank_lt.append(
                serializers.BookBankObjectSerializer(bookbank).data)

        products = Product.objects.filter(store=store)
        for product in products:
            product_lt.append(
                serializers.ProductProfileSerializer(product).data)
            image_q = ProductImages.objects.filter(product=product)
            for image_obj in image_q:
                images_lt.append(
                    serializers.ProductImageSerializer(image_obj).data)

        orders = Order.objects.filter(store=store).order_by("-date_created")
        for order in orders:
            total_item_price = 0
            total_order_quantity = 0
            # * get order_item
            orderItems = OrderItem.objects.filter(order=order)
            for item in orderItems:
                total_item_price += item.price
                total_order_quantity += item.quantity
                orderItem_lt.append(
                    serializers.OrderItemProfileSerializer(item).data)

            # * get order
            order_serial = serializers.OrderProfileSerializer(order).data
            order_serial['total_item_price'] = total_item_price
            order_serial['total_order_price'] = total_item_price + \
                order.box_1+order.box_2+order.shipping
            order_serial['total_order_quantity'] = total_order_quantity
            order_lt.append(order_serial)

        # * get social media QRCode
        qrcodes = SocialQRCode.objects.filter(store=store)
        for qrcode in qrcodes:
            qrcode_serial = serializers.SocialQRCodeSerializer(qrcode).data
            qrcode_serial['social_name'] = getModelChoice(
                qrcode.social, SOCIAL_TYPE)
            qrcode_lt.append(qrcode_serial)

        # * get status count of all order
        fieldname = 'status'
        orderStatus = Order.objects.filter(store=store).values(
            fieldname).order_by(fieldname).annotate(count=Count(fieldname))
        count = {}
        count['store'] = store.id
        for item in orderStatus:
            count[item['status']] = item['count']
        status_lt.append(count)

        # * if all process already set status message to 202
        status_msg = HTTP_200_OK
        status = True

        # * get store location
        store_location = StoreLocation.objects.filter(store=store)
        for location in store_location:
            location_lt.append(
                serializers.StoreLocationSerializer(location).data)

    profile['stores'] = store_lt
    profile['products'] = product_lt
    profile['orders'] = order_lt
    profile['orderItems'] = orderItem_lt
    profile['images'] = images_lt
    profile['bookbank'] = bookbank_lt
    profile['qrcode'] = qrcode_lt
    profile['orders_status'] = status_lt
    profile['location'] = location_lt

    # return Response(profile)
    return Response({'status': status, 'message': msg, 'data': profile}, status=status_msg)


@csrf_exempt
@api_view(["GET", ])
@permission_classes((AllowAny,))
def GetStoreAllAPI(request):
    status = True
    status_msg = HTTP_200_OK
    msg = "access all stores"

    stores = Store.objects.all()
    data = []

    for store in stores:
        store_serial = serializers.StoreAllSerializer(store).data

        store_serial['status'] = getModelChoice(store.status, STATUS_CHOICES)
        store_serial['district'] = getModelChoice(
            store.district, DISTRICT_CHOICES)

        store_serial['owner'] = store.owner.first_name.strip() + \
            " "+store.owner.last_name.strip()

        data.append(store_serial)

    return Response({'status': status, 'message': msg, 'data': data}, status=status_msg)


'''
For Regist new user to system
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((AllowAny,))
def UserRegisAPI(request):
    status = False
    msg = "Invalid data"
    data = {}

    if request.method == 'POST':
        serializer = serializers.UserRegisSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save(request.data)

            # * set current user to trader group
            my_group = Group.objects.get(name='trader')
            my_group.user_set.add(user)

            # add trader profile
            if request.data['citizenid'] == "":
                citizen_id = uuid4().hex[:13]
            else:
                citizen_id = request.data['citizenid']

            Trader.objects.create(
                account=user,
                citizen_id=citizen_id,
                trader_type=request.data['tradertype'],
                store_name=request.data['tradername'],
                phone=request.data['phone'],
            )
            data = {
                'status': 'suceess',
                'email': user.email,
                'username': user.username,
            }
            status = True
            msg = "Your accout has been registered."
        else:
            msg = serializer.errors

    return Response({'status': status, 'message': msg, 'data': data}, status=HTTP_200_OK)


'''
For get order status in current store
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((IsAuthenticated,))
def GetOrderStatusAPI(request):
    if request.method == "POST" and request.data['store'] != None:
        status = False
        msg = "Permission denied"
        data = {}
        order_list = []
        stores = Store.objects.filter(id=request.data['store'])
        for store in stores:
            if request.user == store.owner:
                orders = Order.objects.filter(store=store)
                for order in orders:
                    order_list.append(
                        serializers.OrderProfileSerializer(order).data)

                fieldname = 'status'
                orderStatus = Order.objects.filter(store=store).values(
                    fieldname).order_by(fieldname).annotate(count=Count(fieldname))

                count = {}
                for item in orderStatus:
                    count[item['status']] = item['count']

                data['status'] = count
                data['orders'] = order_list

                status = True
                msg = "Successed"

        return Response({'status': status, 'message': msg, 'data': data}, status=HTTP_200_OK)


'''
For update / insert location in current store
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((IsAuthenticated,))
def UpdateLocationAPI(request):
    data = {}
    status = False
    msg = "Permission denied"

    if request.method == "POST" and request.data['store'] != None:
        store = Store.objects.get(id=int(request.data['store']))
        # convert to float
        location_data = {
            'store': int(request.data['store']),
            'latitude': float(request.data['latitude']),
            'longitude': float(request.data['longitude']),
        }
        if store != None:
            instance = StoreLocation.objects.filter(store=store)
            if instance.count() > 0:
                instance.update(**location_data)
                data = serializers.StoreLocationSerializer(instance[0]).data
            else:
                location = StoreLocation.objects.create(
                    store=store,
                    latitude=location_data['latitude'],
                    longitude=location_data['longitude'],
                )
                data = serializers.StoreLocationSerializer(location).data

            status = True
            msg = "Successed"

    return Response({'status': status, 'message': msg, 'data': data}, status=HTTP_200_OK)


'''
For update order status in current store
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((IsAuthenticated,))
def OrderStatusUpdateAPI(request):
    if request.method == "POST":
        data = {}
        status = False
        msg = "Permission denied"
        if request.data['order_id'] != "" and request.data['status'] != "":
            order_q = Order.objects.filter(id=request.data['order_id'])
            for order in order_q:
                if request.user == order.store.owner:
                    order.status = request.data['status']
                    order.save()

                    # * get order_item
                    total_item_price = 0
                    total_order_quantity = 0
                    orderItems = OrderItem.objects.filter(order=order)
                    for item in orderItems:
                        total_item_price += item.price
                        total_order_quantity += item.quantity

                    data['order'] = serializers.OrderProfileSerializer(
                        order).data
                    data['order']['total_item_price'] = total_item_price
                    data['order']['total_order_price'] = total_item_price + \
                        order.box_1+order.box_2+order.shipping
                    data['order']['total_order_quantity'] = total_order_quantity
                    status = True
                    msg = "Order status has been updated"

        return Response({'status': status, 'message': msg, 'data': data}, status=HTTP_200_OK)


'''
For update shipping in order
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((IsAuthenticated,))
def OrderShippingUpdateAPI(request):
    if request.method == "POST":
        data = {}
        status = False
        check = False
        msg = "Permission denied"
        status_code = HTTP_403_FORBIDDEN

        if request.data['order_id'] != "" and request.data['shipping'] != "":
            orders = Order.objects.filter(id=request.data['order_id'])
            for order in orders:
                if order.store.owner == request.user:
                    order.shipping = request.data['shipping']
                    order.save()

                    data['order'] = serializers.OrderProfileSerializer(
                        order).data
                    check = True

            # update total weight in order model
            if check:
                order_q = Order.objects.filter(id=request.data['order_id'])
                # total_weight = 0
                total_item_price = 0
                total_order_quantity = 0
                for order in order_q:
                    itemAll = OrderItem.objects.filter(order=order)
                    for subItem in itemAll:
                        total_item_price += subItem.price
                        total_order_quantity += subItem.quantity

                    # Get box quantity
                    boxsize_1, boxsize_2 = orderBoxCalculate(
                        total_order_quantity)
                    order.box_1 = Decimal(boxsize_1 * BOX_SIZE_1_PRICE)
                    order.box_2 = Decimal(boxsize_2 * BOX_SIZE_2_PRICE)

                    data['order'] = serializers.OrderProfileSerializer(
                        order).data
                    data['order']['total_item_price'] = total_item_price
                    data['order']['total_order_price'] = total_item_price + \
                        order.box_1+order.box_2+order.shipping
                    data['order']['total_order_quantity'] = total_order_quantity

                    # * if all process already set status message to 202
                    msg = "shipping cost has been updated"
                    status_code = HTTP_200_OK
                    status = True

        return Response({'status': status, 'message': msg, 'data': data}, status=status_code)


'''
For update order weight in order
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((IsAuthenticated,))
def OrderWeightUpdateAPI(request):
    if request.method == "POST":
        data = {}
        status = False
        msg = "Permission denied"
        check = False

        if request.data['order_id'] != "" and request.data['item_id'] != "" and request.data['weight'] != "" and request.data['quantity'] != "":
            item_q = OrderItem.objects.filter(id=request.data['item_id'])
            # update weight & price in order-item
            for item in item_q:
                if item.order.id == int(request.data['order_id']):
                    check = True
                    item.weight = request.data['weight']
                    item.quantity = request.data['quantity']
                    item.price = int(item.price_kg * Decimal(item.weight))

                    item.save()
                    data['orderItems'] = serializers.OrderItemProfileSerializer(
                        item).data

            # update total weight in order model
            if check:
                order_q = Order.objects.filter(id=request.data['order_id'])
                total_weight = 0
                total_item_price = 0
                total_order_quantity = 0
                for order in order_q:
                    itemAll = OrderItem.objects.filter(order=order)
                    for subItem in itemAll:
                        total_weight += subItem.weight
                        total_item_price += subItem.price
                        total_order_quantity += subItem.quantity

                    # calculate shipping cost of current order
                    shipping_cost = shippingCostCalculate(total_weight)

                    # update order model
                    order.shipping = shipping_cost
                    order.weight = total_weight

                    # Get box quantity
                    boxsize_1, boxsize_2 = orderBoxCalculate(
                        total_order_quantity)
                    order.box_1 = Decimal(boxsize_1 * BOX_SIZE_1_PRICE)
                    order.box_2 = Decimal(boxsize_2 * BOX_SIZE_2_PRICE)

                    order.save()

                    data['order'] = serializers.OrderProfileSerializer(
                        order).data
                    data['order']['total_item_price'] = total_item_price
                    data['order']['total_order_price'] = total_item_price + \
                        order.box_1+order.box_2+order.shipping
                    data['order']['total_order_quantity'] = total_order_quantity

                    status = True
                    msg = "Order weight has been updated"

        return Response({'status': status, 'message': msg, 'data': data}, status=HTTP_200_OK)


'''
For Delete store to system
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((IsAuthenticated,))
def DeleteStoreAPI(request):
    if request.method == "POST":
        status = False
        msg = "Permission denied"
        stores = Store.objects.filter(id=int(request.data.get("id")))
        if len(stores) != 0 and stores[0].owner == request.user:
            stores.delete()
            status = True
            msg = "already deleted store"

        return Response({'status': status, 'message': msg}, status=HTTP_200_OK)


'''
For set store statsu api
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((IsAuthenticated,))
def SetStoreStatusAPI(request):
    if request.method == "POST":
        status = False
        msg = "Permission denied"
        data = {}
        status_msg = HTTP_403_FORBIDDEN
        if request.data['store'] != "" and request.data['status'] != "":
            stores = Store.objects.filter(id=request.data['store'])
            for store in stores:
                store.status = request.data['status']
                store.save()
                data['store'] = serializers.StoreSerializer(store).data

                status_msg = HTTP_200_OK
                status = True
                msg = "store status has been changed"

        return Response({'status': status, 'message': msg, 'data': data}, status=status_msg)


'''
For Regist new store to system
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((IsAuthenticated,))
def AddNewStoreAPI(request):
    if request.method == "POST":
        store_msg = {}
        serializer = serializers.StoreRegisSerializer(data=request.data)
        if serializer.is_valid():
            store = serializer.create(request.user, request.data)
            data = {
                'id': store.id,
                'owner': store.owner.id,
                'name': store.name,
                'slogan': store.slogan,
                'about': store.about,
                'phone1': store.phone1,
                'phone2': store.phone2,
                'district': store.district,
                'status': store.status,
            }
            store_msg['store'] = data
            return Response({
                            'status': True,
                            'message': "already registered new store",
                            'data': store_msg,
                            },
                            status=HTTP_200_OK)


'''
For Update store detail
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((IsAuthenticated,))
def UpdateStoreAPI(request):
    if request.method == "POST":
        data = {}
        status = False
        msg = "Invalid User or Store ID"

        serializer = serializers.StoreRegisSerializer(data=request.data)
        if serializer.is_valid():
            stores = Store.objects.filter(id=int(request.data.get("id")))
            serializer.update(stores, request.data)

            store_obj = Store.objects.filter(id=int(request.data.get("id")))
            data['store'] = serializers.StoreRegisSerializer(store_obj[0]).data

            status = True
            msg = "already update stroe"

        return Response({'status': status, 'message': msg, 'data': data}, status=HTTP_200_OK)


'''
For create Product.
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((IsAuthenticated,))
def ProductCreateAPI(request):
    if request.method == 'POST':
        data = {}
        msg = "Invaid product detail or Your store is not approved."
        status = False

        serializer = serializers.ProductSerializer(data=request.data)
        stores = Store.objects.filter(id=int(request.data.get("store_id")))

        if serializer.is_valid() and len(stores) > 0 and stores[0].status == 1:
            store = stores[0]
            product = serializer.create(store, request.data)

            data['product'] = serializers.ProductProfileSerializer(
                product).data
            msg = "Product has been created."
            status = True

        return Response({'status': status, 'message': msg, 'data': data}, status=HTTP_200_OK)


'''
For update Product.
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((IsAuthenticated,))
def ProductUpdateAPI(request):
    if request.method == 'POST':
        msg = "Invaid product detail or Your store is not approved."
        status = False
        data = {}

        serializer = serializers.ProductSerializer(data=request.data)
        stores = Store.objects.filter(id=int(request.data.get("store_id")))
        product = Product.objects.filter(id=request.data.get('product_id'))

        if serializer.is_valid() and stores[0].status == 1 and len(product) > 0:
            product = serializer.update(product, request.data)
            product_obj = Product.objects.filter(
                id=request.data.get('product_id'))
            status = True
            data['product'] = serializers.ProductProfileSerializer(
                product_obj[0]).data
            msg = "Product has been updated."

        return Response({'status': status, 'message': msg, 'data': data}, status=HTTP_200_OK)


'''
For delete Product.
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((IsAuthenticated,))
def ProductDeleteAPI(request):
    if request.method == "POST":
        status = False
        msg = "Permission Denied"
        status_code = HTTP_403_FORBIDDEN

        if request.data['id'] != None:
            products = Product.objects.filter(id=int(request.data['id']))
            for product in products:
                if product.store.owner == request.user:
                    product.delete()
                    status = True
                    msg = "already deleted product"
                    status_code = HTTP_200_OK

        return Response({'status': status, 'message': msg}, status=status_code)


'''
For add new product images
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((IsAuthenticated,))
def ProductImageAddAPI(request):
    if request.method == "POST":
        status = False
        msg = "Can not upload image"
        data = []

        products = Product.objects.filter(id=request.data['product'])

        if len(products) != 0 and request.data['image'] != None:
            # * Get images list from multipartFile request
            images = request.FILES.getlist('image')

            for product in products:
                if product.store.owner == request.user:
                    for image in images:
                        productImage = ProductImages.objects.create(
                            product=product,
                            image=image
                        )
                        data.append(serializers.ProductImageSerializer(
                            productImage).data)

                    msg = "Product image has beend uploaded"
                    status = True

        return Response({'status': status, 'message': msg, 'data': data}, status=HTTP_200_OK)
    else:
        status = False
        msg = "error"
        return Response({'status': status, 'message': msg}, status=HTTP_400_BAD_REQUEST)


'''
For delete product images
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((IsAuthenticated,))
def ProductImageDeleteAPI(request):
    if request.method == "POST" and request.data['product'] != None and request.data['image'] != None:
        status = False
        msg = "Can not delete image"
        status_msg = HTTP_403_FORBIDDEN

        products = Product.objects.filter(id=request.data['product'])
        for product in products:
            if product.store.owner == request.user:
                images = ProductImages.objects.filter(id=request.data['image'])
                for image in images:
                    image.delete()
                    status = True
                    msg = "Product image has been deleted"
                    status_msg = HTTP_200_OK

        return Response({'status': status, 'message': msg}, status=status_msg)


'''
For Create Bookbank.
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((IsAuthenticated,))
def BookBankCreateAPI(request):
    if request.method == "POST":
        status = False
        msg = "Can not create bookbank"
        data = {}

        serializer = serializers.BookBankSerializer(data=request.data)
        if serializer.is_valid:
            store_obj = Store.objects.get(id=request.data['store'])
            bookbank = serializer.create(store_obj, request.data)
            data['bookbank'] = serializers.BookBankObjectSerializer(
                bookbank).data
            status = True
            msg = "Bookbank has been create"

        return Response({'status': status, 'message': msg, 'data': data}, status=HTTP_200_OK)


'''
For Delete Bookbank.
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((IsAuthenticated,))
def BookBankDeleteAPI(request):
    if request.method == "POST":
        status = False
        msg = "Can not delete bookbank"
        bookbank_qs = BookBank.objects.filter(id=request.data['id'])
        for bookbank in bookbank_qs:
            if request.user == bookbank.store.owner:
                bookbank.delete()
                status = True
                msg = "Bookbank has been deleted"
        return Response({'status': status, 'message': msg}, status=HTTP_200_OK)


'''
For Update Bookbank.
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((IsAuthenticated,))
def BookBankUpdateAPI(request):
    if request.method == "POST":
        status = False
        msg = "Can not update bookbank"
        data = {}

        bookbanks = BookBank.objects.filter(id=request.data['id'])
        if len(bookbanks) != 0:
            serializer = serializers.BookBankSerializer(data=request.data)
            if serializer.is_valid:
                check = serializer.update(bookbanks, request.data)
                bookbank = BookBank.objects.get(id=request.data['id'])

                data['bookbank'] = serializers.BookBankObjectSerializer(
                    bookbank).data
                status = True
                msg = "Bookbank has been updated"

        return Response({'status': status, 'message': msg, 'data': data}, status=HTTP_200_OK)


'''
For check transfer.
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((IsAuthenticated,))
def TransferCheckAPI(request):
    if request.method == "POST":
        status = False
        msg = "Not found transfer slip"
        data = {}
        status_code = HTTP_200_OK

        order_q = Order.objects.filter(id=request.data['order'])
        for order in order_q:
            if order.store.owner == request.user:
                transfer_q = TransferNotification.objects.filter(order=order)
                if len(transfer_q) > 0:
                    for transfer in transfer_q:
                        status = True
                        msg = "show order transfer notification"
                        data['transfer'] = serializers.TransferNotificationSerializer(
                            transfer).data
                else:
                    status_code = HTTP_404_NOT_FOUND
            else:
                msg = "Permission denied"
                status_code = HTTP_403_FORBIDDEN

        return Response({'status': status, 'message': msg, 'data': data}, status=status_code)


'''
For add new QRCode images
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((IsAuthenticated,))
def QRCodeAddAPI(request):
    status = False
    msg = "Can not upload image"
    data = {}
    status_msg = HTTP_400_BAD_REQUEST

    if request.method == "POST":
        stores = Store.objects.filter(id=request.data['store'])
        if len(stores) != 0 and request.data['image'] != None and request.data['social'] != None:
            # * Get images list from multipartFile request
            images = request.FILES.getlist('image')

            for store in stores:
                if store.owner == request.user:
                    for image in images:
                        qrcode_obj = SocialQRCode.objects.create(
                            store=store,
                            social=request.data['social'],
                            qr_code=image,
                        )
                        data = serializers.SocialQRCodeSerializer(
                            qrcode_obj).data
                        msg = "QRCode has beend uploaded"
                        status = True
                        status_msg = HTTP_200_OK

    return Response({'status': status, 'message': msg, 'data': data}, status=status_msg)


'''
For delete social QRCode.
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((IsAuthenticated,))
def QRCodeDeleteAPI(request):
    if request.method == "POST":
        status = False
        msg = "Permission denied"
        data = {}
        status_code = HTTP_403_FORBIDDEN

        if request.data['store'] != None and request.data['qrcode'] != None:
            store_obj = Store.objects.filter(id=request.data['store'])
            qrcode_obj = SocialQRCode.objects.filter(id=request.data['qrcode'])
            for qrcode in qrcode_obj:
                if len(store_obj) != 0 and qrcode.store == store_obj[0]:
                    qrcode.delete()
                    status = True
                    msg = "QRCode has been deleted."
                    status_code = HTTP_200_OK

        return Response({'status': status, 'message': msg, 'data': data}, status=status_code)


'''
For Check Citizen ID is already exist
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((AllowAny,))
def CheckCitizenIDAPI(request):
    citizen_id = request.data.get("citizenid")
    if citizen_id is None:
        return Response({'error': 'Please Citizen ID'},
                        status=HTTP_400_BAD_REQUEST)
    else:
        msg = "ID not exist"
        found = False

        traders = Trader.objects.filter(citizen_id=citizen_id)
        for trader in traders:
            if trader.citizen_id != "":
                msg = "ID already exist"
                found = True

        return Response({'status': found, 'message': msg},
                        status=HTTP_200_OK)


'''
For Check Email already exist
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((AllowAny,))
def CheckEmailAPI(request):
    email = request.data.get("email")
    if email is None:
        return Response({'error': 'Please Citizen ID'},
                        status=HTTP_400_BAD_REQUEST)
    else:
        msg = "Email not exist"
        found = False

        users = User.objects.filter(email=email)
        for user in users:
            if user.email != "":
                msg = "Email already exist"
                found = True

        return Response({'status': found, 'message': msg},
                        status=HTTP_200_OK)


'''
For user login via API
'''


@csrf_exempt
@api_view(["POST", ])
@permission_classes((AllowAny,))
def LoginAPI(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'},
                        status=HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if not user:
        return Response({'error': 'Invalid Credentials'}, status=HTTP_404_NOT_FOUND)

    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key}, status=HTTP_200_OK)
