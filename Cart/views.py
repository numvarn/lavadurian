import requests
import json

from django import forms
from django.shortcuts import render, redirect, HttpResponse
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required

from Store.models import Product, BookBank
from Store.models import ACCOUNT_TYPE, BANK, GENE_CHOICES, GRADE_CHOICES, PRODUCT_STATUS_CHOICES, Review
from Cart.models import AddressBook, Cart, CartItem, ORDER_STATUS_CHOICES, Order, OrderBox, OrderItem, OrderMessage, OrderTracking, ReceiveAddress, TRACKER_STATUS_CHOICES, TransferNotification
from Cart.form import OrderItemForm, OrderMessageForm, OrderTrackingForm, ReceiveAddressForm, SetOrderStatus, TransferNotificationForm

from Cart.choice import PROVINCE_CHOICE
from Store.forms import ReviewForm
from lavadurian import settings
from django.core.mail import send_mail

from math import ceil
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# This box price
# modify in 19-march-2021
BOX_SIZE_1_PRICE = 30
BOX_SIZE_2_PRICE = 38


def cartShow(request):
    session_key = request.session.session_key
    query = []
    items = []
    query = Cart.objects.filter(session_key=session_key)
    shipping_cost = 0
    total_cost = 0

    summation = 0
    total_weight = 0

    if len(query) != 0:
        cart = query[0]
        items = CartItem.objects.filter(cart=cart)

        for item in items:
            item.status_choice = getModelChoice(
                item.product.status, PRODUCT_STATUS_CHOICES)
            item.grade_choice = getModelChoice(
                item.product.grade, GRADE_CHOICES)
            item.gene_choice = getModelChoice(item.product.gene, GENE_CHOICES)

            # total price
            item.total_price = (item.product.price *
                                item.product.weight) * item.quantity
            summation += item.total_price

            # total weight
            total_weight += item.quantity * item.product.weight

        # ------------------------------------------------
        # shipping cost
        shipping_cost = shippingCostCalculate(total_weight)
        # total_cost
        total_cost = summation + shipping_cost

    context = {
        'title': "ตระกร้าสินค้า",
        'subtitle': 'รายการสินค้าภายในตะกร้าสินค้าที่ท่านเลือกซื้อ',
        'items': items,
        'total_weight': total_weight,
        'summation': summation,
        'shipping_cost': shipping_cost,
        'total_cost': total_cost,
    }
    return render(request, 'cart_show.html', context)


def cartAdd(request, id):
    product = Product.objects.get(id=id)
    session_key = request.session.session_key

    if product.values > 0:
        if session_key != "" and session_key != None:
            query = []
            query = Cart.objects.filter(session_key=session_key)
            if len(query) == 0:
                cart = Cart(session_key=session_key)
                cart.save()
            else:
                cart = query[0]

            query = []
            query = CartItem.objects.filter(Q(cart=cart) & Q(product=product))
            if len(query) == 0:
                chartItem = CartItem(
                    cart=cart,
                    product=product
                )
                chartItem.save()
        else:
            messages.error(
                request, "ไม่สามารถสร้าง Session ได้กรุณาทำการ Loing เข้าสู่ระบบก่อนซื้อสินค้า")
            return redirect("/members/login")
    else:
        messages.error(
            request, "สินค้าที่ท่านเลือกปัจจุบันไม่มีของอยู่ในสต๊อกสินค้าแล้ว, ปริมาณสินค้าเท่ากับ 0")

    return redirect("/cart/show/")


def cartDelete(request, id):
    session_key = request.session.session_key
    item = CartItem.objects.get(id=id)
    if item != None:
        if item.cart.session_key == session_key:
            item.delete()
    return redirect("/cart/show/")


def cartClear(request):
    session_key = request.session.session_key
    query = []
    query = Cart.objects.filter(session_key=session_key)
    if len(query) != 0:
        cart = query[0]
        items = CartItem.objects.filter(cart=cart)
        if len(items) != 0:
            for item in items:
                item.delete()
    return redirect("/cart/show/")


def itemUpdate(request):
    for param, vals in request.GET.lists():
        item = CartItem.objects.get(id=param)
        for val in vals:
            if item.product.values >= int(val):
                item.quantity = val
                item.save()
            else:
                messages.error(
                    request, "จำนวนสินค้าในสต๊อกไม่เพียงพอต่อจำนวนที่ท่านเลือก")

    return redirect("/cart/show/")


''''
Checkout Page
- Check user authentication
- Add receiver address
- Comfirm order checkout
'''
# @login_required


def cartCheckout(request):
    session_key = request.session.session_key
    address_form = ''
    addressbook = ''
    province = []
    query = []
    items = []
    shipping_cost = 0
    query = Cart.objects.filter(session_key=session_key)

    summation = 0
    total_weight = 0
    total_values = 0

    # Cart has exist
    if len(query) != 0:
        cart = query[0]
        items = CartItem.objects.filter(cart=cart)

        cart.item_price = 0

        # If cart is empty show cart page
        if len(items) != 0:
            for item in items:
                item.status_choice = getModelChoice(
                    item.product.status, PRODUCT_STATUS_CHOICES)
                item.grade_choice = getModelChoice(
                    item.product.grade, GRADE_CHOICES)
                item.gene_choice = getModelChoice(
                    item.product.gene, GENE_CHOICES)

                # total price
                item.total_price = (item.product.price *
                                    item.product.weight) * item.quantity
                summation += item.total_price

                # total weight
                item.total_weight = item.quantity * item.product.weight
                cart.item_price += item.product.price * \
                    (item.quantity * item.product.weight)
                total_weight += item.total_weight
                total_values += item.quantity

            # If not authenticate user
            if request.user.is_authenticated:
                user = User.objects.get(id=request.user.id)
                address_form = ReceiveAddressForm(initial={'receiver': user})

                # get list of address book
                query = AddressBook.objects.filter(owner=user)
                if len(query) != 0:
                    addressbook = query[0]
                    for address in addressbook.receive_address.all():
                        for choice in PROVINCE_CHOICE:
                            if choice[0] == address.province:
                                province.append(choice[1])
                                break

            # รวมค่าขนส่ง
            shipping_cost = shippingCostCalculate(total_weight)
            summation += shipping_cost

            # Get box quantity
            cart.boxsize_1, cart.boxsize_2 = orderBoxCalculate(total_values)
            cart.box_1_cost = cart.boxsize_1 * BOX_SIZE_1_PRICE
            cart.box_2_cost = cart.boxsize_2 * BOX_SIZE_2_PRICE

            # รวมค่ากล่อง
            summation += int(cart.box_1_cost) + int(cart.box_2_cost)

            context = {
                'title': "ยืนยันการสั่งซื้อ",
                'subtitle': 'ทำการตรวจสอบและยืนยันการสั่งซื้อรายการสินค้าภายในตะกร้า',
                'cart': cart,
                'items': items,
                'total_weight': total_weight,
                'total_values': total_values,
                'summation': summation,
                'address_form': address_form,
                'addressbook': addressbook,
                'province': province,
                'shipping_cost': shipping_cost,
            }

            return render(request, 'cart_checkout.html', context)
        else:
            messages.error(
                request, 'ไม่สามารถยืนยันการสั่งซื้อได้ เนื่องจากตะกร้ายังไม่มีรายการสินค้า')
            return redirect("/cart/show/")
    else:
        return redirect("/")


'''
Show Complete Order
- Create Order list
- Clear all items in cart
- Clear cart
'''


@login_required
def cartProcessOrder(request):
    if request.method == 'POST':
        receive_address = request.POST.get('address')
        customer_request = request.POST.get('customer_request')

        session_key = request.session.session_key
        query = Cart.objects.filter(session_key=session_key)

        storeList = []

        cart = None
        if len(query) != 0:
            cart = query[0]
            items = CartItem.objects.filter(cart=cart)

            # Separate Order by Store
            for item in items:
                if item.product.store not in storeList:
                    storeList.append(item.product.store)

            for store in storeList:
                # Create Order
                total_weight = 0
                shipping_cost = 0

                order = Order.objects.create(
                    owner=request.user,
                    store=store,
                    receive_address=ReceiveAddress.objects.get(
                        id=receive_address),
                    customer_request=customer_request
                )

                total_quantity = 0
                # Create OrderItem in current store
                for item in items:
                    if item.product.store == store:
                        orderItem = OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            quantity=item.quantity,
                            price=(item.product.price *
                                   item.product.weight) * item.quantity,
                            price_kg=item.product.price,
                            weight=item.product.weight * item.quantity,
                        )

                        total_quantity += orderItem.quantity
                        total_weight = total_weight + \
                            (item.product.weight * item.quantity)

                        # Cut off product values
                        # ตัดสต๊อกสินค้าในคลัง
                        if orderItem != None:
                            product = Product.objects.get(id=item.product.id)
                            product.values -= item.quantity
                            product.save()

                # save to orderbox model
                boxsize_1, boxsize_2 = orderBoxCalculate(total_quantity)
                orderbox = OrderBox.objects.create(
                    order=order,
                    boxsize_1=boxsize_1,
                    boxsize_2=boxsize_2
                )

                # calculate shipping cost of current order
                shipping_cost = shippingCostCalculate(total_weight)

                # save to order model
                order.shipping = shipping_cost
                order.weight = total_weight
                order.box_1 = boxsize_1 * BOX_SIZE_1_PRICE
                order.box_2 = boxsize_2 * BOX_SIZE_2_PRICE
                order.save()

                # Send email to store owner
                # sendMailStoreApproved(store)

            # Clear Cart and Items
            cart.delete()

            return redirect("/order/my/")
        else:
            return redirect("/")
    else:
        messages.error(
            request, 'ไม่สามารถยืนยันการสั่งซื้อได้ เนื่องจากตะกร้ายังไม่มีรายการสินค้า')
        return redirect("/")


'''
Calcuate OrderBox
'''


def orderBoxCalculate(total_quantity):
    boxsize_1 = 0
    boxsize_2 = 0

    if total_quantity == 1:
        boxsize_1 = 1
    else:
        if total_quantity % 2 != 0:
            boxsize_1 = 1
            boxsize_2 = (total_quantity - 1) / 2
        else:
            boxsize_2 = total_quantity / 2

    return boxsize_1, boxsize_2


'''
Show Current User Order
'''


@login_required
def orderMy(request):
    orders = Order.objects.filter(owner=request.user).order_by('-date_created')

    # get list of address book
    province = []
    addressbook = None
    query = AddressBook.objects.filter(owner=request.user)
    if len(query) != 0:
        addressbook = query[0]
        for address in addressbook.receive_address.all():
            province.append(getModelChoice(address.province, PROVINCE_CHOICE))

    for order in orders:
        order.total_price = 0
        order.status_choice = getModelChoice(
            order.status, ORDER_STATUS_CHOICES)
        items = OrderItem.objects.filter(order=order)
        for item in items:
            order.total_price += item.price

        # * ราคาทุเรียน + ค่าขนส่ง
        order.total_price += order.shipping

        # * ราคาทุเรียน + ค่าขนส่ง + ค่ากล่อง
        order.total_price += order.box_1 + order.box_2

        # * Get transfer notif is it exist
        transfer = None
        order.transfer_notif = ''
        query = TransferNotification.objects.filter(order=order)
        if len(query) != 0:
            transfer = query[0]
            order.transfer_notif = transfer.image.url

    context = {
        'title': "รายการสั่งซื้อสินค้าของฉัน",
        'subtitle': 'รายการสั่งซื้อสินค้าของฉันที่ได้ดำเนินไปการแล้ว สามารถตรวจสอบรายละเอียดและสถานะได้จากหน้านี้',
        'orders': orders,
        'addressbook': addressbook,
        'province': province,
    }
    return render(request, 'order_my.html', context)


'''
Show Order detail
'''


@login_required
def orderDetail(request, id):
    query = Order.objects.filter(id=id)
    if len(query) != 0:
        order = query[0]
    else:
        messages.error(
            request, "คุณไม่มีสิทธิ์เข้าถึงรายละเอียดของคำสั่งซื้อนี้")
        return redirect('/cart/show/')

    order.item_price = 0

    total_price = 0
    total_weight = 0
    total_values = 0
    review_form = ''
    form_tracking = ''
    product_review = None
    reviews = None
    orderbox = None

    if order != None and (order.owner == request.user or order.store.owner == request.user or request.user.is_superuser):
        items = OrderItem.objects.filter(order=order)

        order.province_choice = getModelChoice(
            order.receive_address.province, PROVINCE_CHOICE)
        order.status_choice = getModelChoice(
            order.status, ORDER_STATUS_CHOICES)
        order.status_display = getModelChoice(
            order.status, ORDER_STATUS_CHOICES)

        for item in items:
            item.grade_choice = getModelChoice(
                item.product.grade, GRADE_CHOICES)
            item.status_choice = getModelChoice(
                item.product.status, PRODUCT_STATUS_CHOICES)

            item.total_weight = item.weight
            order.item_price += item.price
            total_price += item.price
            total_weight += item.total_weight
            total_values += item.quantity

        # ค่าใช้จ่าย - รวมค่าขนส่ง
        total_price += order.shipping

        # ค่าใช้จ่าย - รวมค่ากล่อง
        total_price += order.box_1 + order.box_2

        form = ''
        form_msg = ''
        transfer_notif = ''
        bookbanks = None

        # เจ้าของร้านค้า
        if order.store.owner == request.user:
            # Form for set order status
            if request.method == "POST":
                form = SetOrderStatus(
                    request.POST, request.FILES, instance=order)
                if form.is_valid:
                    order = form.save()

                    # Send email to customer
                    order.status_display = getModelChoice(
                        order.status, ORDER_STATUS_CHOICES)
                    # sendMailOrderStatusChanged(order)

                    return redirect("/order/detail/"+str(order.id))
            else:
                form = SetOrderStatus(instance=order)
                form_msg = OrderMessageForm(initial={'order': order})

                # Tracker : check tracking is exist
                query = OrderTracking.objects.filter(order=order)
                if len(query) > 0:
                    tracker = query[0]
                    form_tracking = OrderTrackingForm(instance=tracker)
                else:
                    form_tracking = OrderTrackingForm(
                        initial={'order': order, 'store': order.store})

                if order.status >= 5:
                    # Show transfers nitification bill
                    query = TransferNotification.objects.filter(
                        order=order).order_by('-date_created')
                    if len(query) != 0:
                        transfer_notif = query[0]
                        transfer_notif.bank_choice = getModelChoice(
                            transfer_notif.bookbank.bank, BANK)
        # ผู้ซื้อ
        elif order.owner == request.user:
            if order.status == 3 or order.status == 2:
                # Show transfers nitification form
                form = TransferNotificationForm(
                    initial={'order': order, 'store': order.store})
                form.fields['order'].widget = forms.HiddenInput()

                # Get book bank
                bookbanks = BookBank.objects.filter(
                    store=order.store).order_by('-date_created')
                for bookbank in bookbanks:
                    bookbank.bank_choice = getModelChoice(bookbank.bank, BANK)
                    bookbank.account_type_choice = getModelChoice(
                        bookbank.account_type, ACCOUNT_TYPE)
            else:
                # Show transfers nitification bill
                query = TransferNotification.objects.filter(
                    order=order).order_by('-date_created')
                if len(query) != 0:
                    transfer_notif = query[0]
                    transfer_notif.bank_choice = getModelChoice(
                        transfer_notif.bookbank.bank, BANK)

            # Reviews Form
            if request.GET.get("product") != None:
                product_id = request.GET.get("product")
                product_review = Product.objects.get(id=product_id)

                # set form and set initial values
                review_form = ReviewForm(initial={'store': order.store,
                                                  'reviewer': request.user,
                                                  'product': product_review,
                                                  'order': int(order.id),
                                                  'score': 1}
                                         )
                # hide somefield
                review_form.fields['store'].widget = forms.HiddenInput()
                review_form.fields['reviewer'].widget = forms.HiddenInput()
                review_form.fields['product'].widget = forms.HiddenInput()
                review_form.fields['order'].widget = forms.HiddenInput()
                review_form.fields['score'].widget = forms.HiddenInput()

        # Get Review
        if 4 <= order.status < 8:
            reviews = Review.objects.filter(
                order=order.id).order_by('-date_review')

        # Get Message
        order_messages = OrderMessage.objects.filter(
            order=order).order_by('-date_created')

        # Get Tracking Number
        tracker = ''
        query = OrderTracking.objects.filter(order=order)
        if len(query) > 0:
            tracker = query[0]
            tracker.status_choice = getModelChoice(
                tracker.status, TRACKER_STATUS_CHOICES)

        # Get orderbox
        query = OrderBox.objects.filter(order=order)
        if len(query) > 0:
            orderbox = query[0]

        context = {
            'title': "รายระเอียดการสั่งซื้อ",
            'subtitle': 'แสดงรายระเอียดการสั่งซื้อที่ดำเนินการสั่งสำเร็จแล้ว',
            'order': order,
            'items': items,
            'total_price': total_price,
            'total_weight': total_weight,
            'total_values': total_values,
            'form': form,
            'form_msg': form_msg,
            'form_tracking': form_tracking,
            'transfer_notif': transfer_notif,
            'bookbanks': bookbanks,
            'review_form': review_form,
            'product_review': product_review,
            'reviews': reviews,
            'order_messages': order_messages,
            'tracker': tracker,
            'orderbox': orderbox,
        }

        return render(request, 'order_detail.html', context)
    else:
        return redirect("/")


@login_required
def trackingSave(request):
    if request.method == "POST":
        order_id = request.POST.get("order")
        order = Order.objects.get(id=order_id)

        query = OrderTracking.objects.filter(order=order)
        if len(query) > 0:
            tracker = query[0]
            form = OrderTrackingForm(
                request.POST, request.FILES, instance=tracker)
        else:
            form = OrderTrackingForm(request.POST, request.FILES)

        if form.is_valid:
            form.save()
            if order.status < 6:
                order.status = 6
                order.save()

            # Send email to customer
            order.status_display = getModelChoice(
                order.status, ORDER_STATUS_CHOICES)
            # sendMailOrderStatusChanged(order)

            messages.success(request, "บันทึกหมายเลขพัสดุแล้ว")
            return redirect('/order/detail/'+str(order_id))


@login_required
def transferNotifSave(request):
    # Form transfer notification
    if request.method == "POST":
        order_id = request.POST.get("order")
        order = Order.objects.get(id=order_id)
        # Submit transfers nitification form
        form = TransferNotificationForm(request.POST, request.FILES)
        if form.is_valid:
            transfer = form.save()
            order.status = 5
            order.save()
            return redirect('/order/my/')


@login_required
def reviewAdd(request):
    if request.method == "POST":
        order_id = request.POST.get("order")
        rating = request.POST.get("rating")

        review_form = ReviewForm(request.POST, request.FILES)
        if review_form.is_valid:
            review = review_form.save()
            review.score = rating
            review.save()

        return redirect("/order/detail/"+str(order_id))


@login_required
def notifDelete(request):
    if request.method == "POST":
        notif_id = request.POST.get("transfer_notif")
        notif = TransferNotification.objects.get(id=notif_id)
        if notif != None and notif.order.owner == request.user:
            order = Order.objects.get(id=notif.order.id)
            order.status = 3
            order.save()
            notif.delete()
            return redirect("/order/my/")
        return redirect("/order/my/")
    else:
        return redirect("/order/my/")


@login_required
def cartReceiverAddress(request):
    if request.method == 'POST':
        user = User.objects.get(id=request.user.id)
        form = ReceiveAddressForm(request.POST, request.FILES)

        if form.is_valid:
            address = form.save()
            query = AddressBook.objects.filter(owner=user)
            if len(query) != 0:
                book = query[0]
            else:
                book = AddressBook(owner=user)
                book.save()

            book.receive_address.add(address)
            return redirect("/cart/checkout/")
        else:
            return redirect("/cart/checkout/")


@login_required
def orderDelete(request, id):
    query = Order.objects.filter(id=id)
    if len(query) > 0:
        order = query[0]
        print("order status : {} : {}".format(order.status, id))
        if order.owner == request.user and order.status < 4:
            order.delete()
            return redirect("/order/my/")
        else:
            messages.error(request, "Error, Permission denied.")
            return redirect("/order/my/")
    else:
        return redirect("/order/my/")


def cartLogin(request):
    if request.method == 'POST':
        # Get current cart by using current user session key
        session_key = request.session.session_key
        query = Cart.objects.filter(session_key=session_key)
        cart = query[0]

        user = authenticate(
            username=request.POST.get('user'),
            password=request.POST.get('password')
        )
        if user is not None:
            if user.is_active:
                login(request, user)

                # update cart session_key for current user
                cart.session_key = request.session.session_key
                cart.save()

                return redirect("/cart/checkout/")
            else:
                messages.error(request, 'This account has been disabled!')
                return redirect("/cart/checkout/")
        else:
            messages.error(
                request, 'มีข้อผิดพลาด กรุณาตรวจสอบ username/password')
            return redirect("/cart/checkout/")


def cartRegisterCustomer(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        pass1 = request.POST.get('password1')

        if cartCheckUserExist(email):
            user = User.objects.create_user(
                username=email,
                first_name=firstname,
                last_name=lastname,
                email=email,
                password=pass1,
            )

            my_group = Group.objects.get(name='customer')
            my_group.user_set.add(user)

            if user is not None:
                messages.error(
                    request, 'บัญชีผู้ซื้อถูกสร้างแล้ว ล็อคอินเพื่อใช้งานได้ทันที')
                return redirect("/cart/checkout/")
        else:
            messages.error(request, 'มีปัญชีผู้ใช้นี้อยู่ในระบบอยู่แล้ว')
            return redirect("/cart/checkout/")

        return redirect("/cart/checkout/")


@login_required
def orderEditWeight(request, id):
    item = OrderItem.objects.get(id=id)
    if request.method == "POST":
        form = OrderItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid:
            item = form.save()
            item.price = int(item.price_kg * item.weight)
            item.save()

            # update total weight in order model
            total_weight = 0
            order = Order.objects.get(id=item.order.id)
            itemAll = OrderItem.objects.filter(order=order)
            for subItem in itemAll:
                total_weight += subItem.weight

            # calculate shipping cost of current order
            shipping_cost = shippingCostCalculate(total_weight)

            # update order model
            order.shipping = shipping_cost
            order.weight = total_weight
            order.save()

            return redirect("/order/detail/"+str(item.order.id))

    if item.order.store.owner == request.user:
        product = item.product
        product.gene_choice = getModelChoice(product.gene, GENE_CHOICES)
        product.grade_choice = getModelChoice(product.grade, GRADE_CHOICES)
        product.status_choice = getModelChoice(
            product.status, PRODUCT_STATUS_CHOICES)

        product.price_total = product.values * product.price

        context = {
            'title': "รายระเอียดการสั่งซื้อ ",
            'subtitle': 'แสดงรายระเอียดการสั่งซื้อที่ดำเนินการสั่งสำเร็จแล้ว',
            'product': product,
            'quantity': item.quantity,
            'order_id': item.order.id,
            'form': OrderItemForm(instance=item)
        }

        return render(request, "order_edit_weight.html", context)
    else:
        return redirect("/")


@login_required
def orderMessageSave(request):
    if request.method == "POST":
        order_id = request.POST.get("order")
        form_msg = OrderMessageForm(request.POST, request.FILES)
        if form_msg.is_valid:
            form_msg.save()
            messages.success(request, "บันทึกข้อมูลสำเร็จ")
            return redirect("/order/detail/"+str(order_id))
    else:
        messages.error(request, "Access Denied")
        return redirect("/")


def getShippingStatus(request):
    api_token_url = 'https://trackapi.thailandpost.co.th/post/api/v1/authenticate/token'
    api_track_url = 'https://trackapi.thailandpost.co.th/post/api/v1/track'

    # get items from tracker
    items_list = []
    query = OrderTracking.objects.filter(Q(status__lt=501))[:100]
    if len(query) > 0:
        for tracker in query:
            items_list.append(tracker.tracker)

        # @Step 1 : Get user token
        header_token = {
            'Authorization': 'Token IgVVNuGWRcW!P4RvJGMwGwS+HVB9UTV=N|QFQ#V?SKMmOLV?CkA_Y:TCW!IUWmHEG5Q8UrKiV=GBMiNvL|K2Q/KEG4X?GkZ:B%VK',
            'Content-Type': 'application/json',
        }

        response = requests.post(
            api_token_url, headers=header_token, verify=False)
        data_json = response.json()

        # Get token
        token = "Token "+data_json['token']

        # @Step 2 : Get Tracking items status
        header_items = {
            'Authorization': token,
            'Content-Type': 'application/json',
        }

        items = {
            "status": "all",
            "language": "TH",
            "barcode": items_list
        }

        response = requests.post(api_track_url, data=json.dumps(
            items), headers=header_items, verify=False)

        # Process result
        resultsJson = response.json()
        trackItems = resultsJson['response']['items']

        for itemID in items_list:
            status = trackItems[itemID][-1]['status']
            query = OrderTracking.objects.filter(tracker=itemID)
            if len(query) > 0:
                tracker = query[0]
                tracker.status = int(status)
                tracker.save()

                if int(status) == 501:
                    # Set order to end process status
                    tracker.order.status = 7
                    tracker.order.save()

        return HttpResponse(response, content_type='application/json')
    else:
        return HttpResponse("Have no any items to track yet.")

# Shipping Cost
# Promotion form thaipost


def shippingCostCalculate(total_weight):
    cost = 0
    cost += shippingCost(total_weight)
    return cost


def shippingCost(total_weight):
    cost = 0
    total_weight = ceil(total_weight)

    if total_weight <= 5:
        cost = 40
    elif total_weight <= 6:
        cost = 48
    else:
        cost = 48 + ((total_weight - 6) * 8)

    return cost

# Check User or Email is Already Exist


def cartCheckUserExist(email):
    user = User.objects.filter(
        Q(username__icontains=email) |
        Q(email__icontains=email)
    )
    if len(user) != 0:
        return False
    else:
        return True

# Mapping Chice : int to string


def getModelChoice(intValue, choices):
    choice_result = ''
    for choice in choices:
        if choice[0] == intValue:
            choice_result = choice[1]
            break
    return choice_result

# Send email
# to store owner
# wher order was submited


def sendMailStoreApproved(store):
    subject = 'มีการสั่งซื้อจาก www.lavadurian.com'
    message = 'ร้าน '+store.name+" มียอดการสั่งซื้อ 1 รายการ"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [store.owner.email, ]
    send_mail(subject, message, email_from, recipient_list)

# Send email
# to customer
# wherm order status was changed


def sendMailOrderStatusChanged(order):
    subject = 'แจ้งสถานะคำสั่งซื้อบน www.lavadurian.com'
    message = 'ร้าน '+order.store.name + \
        " ได้ปรับสถานะคำสั่งซื้อของท่านเป็น "+order.status_display+" แล้ว"

    context = {
        'message': message,
        'order': order,
        'link': 'https://www.lavadurian.com/order/detail/'+str(order.id),
        'link_transfer': 'https://www.lavadurian.com/order/detail/'+str(order.id)+"#transfer",
    }

    # get bookbank
    if order.status == 3:
        bookbanks = []
        query = BookBank.objects.filter(store=order.store)
        if len(query) > 0:
            bookbanks = query
            for bookbank in bookbanks:
                bookbank.bank_choice = getModelChoice(bookbank.bank, BANK)
                bookbank.account_type_choice = getModelChoice(
                    bookbank.account_type, ACCOUNT_TYPE)
            context['bookbanks'] = bookbanks

    elif order.status == 6:
        tracker = []
        query = OrderTracking.objects.filter(order=order)
        if len(query) > 0:
            tracker = query[0]
            context['tracker'] = tracker

    html_message = render_to_string('mail_template.html', context)
    plain_message = strip_tags(html_message)

    email_from = settings.EMAIL_HOST_USER
    recipient_list = [order.owner.email, ]

    send_mail(subject, plain_message, email_from,
              recipient_list, html_message=html_message)


'''
จำข้อมูลรายชื่อที่อยู่ ผู้ซื้อ ออกมาในรูปแบบของ excel
'''


def exportReceiveAddress(request):
    import pandas as pd

    address = ReceiveAddress.objects.all().order_by('id')
    df = pd.DataFrame(list(address.values()))

    receiver_list = []
    index_list = []
    for index, row in df.iterrows():
        if row['phone'].strip() not in receiver_list:
            receiver_list.append(row['phone'].strip())
        else:
            index_list.append(index)

    df.drop(index_list, axis=0, inplace=True)

    df.to_csv("/Users/phisan/Desktop/address.csv")
    return HttpResponse("export Receive Address")
