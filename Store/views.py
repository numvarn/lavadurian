import datetime
from multiprocessing import context
import pytz
import os

from django.shortcuts import redirect, render, HttpResponse
from django import forms
from datetime import date
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms.models import modelformset_factory
from django.db.models import Avg, Count, Q, Sum
from django.core.mail import send_mail

from Store.forms import AddProductForm, BankForm, CreateStoreForm, ProductImageForm, StoreCertificateForm
from Store.models import ACCOUNT_TYPE, BANK, GENE_CHOICES, GRADE_CHOICES, PRODUCT_STATUS_CHOICES, SOCIAL_TYPE, STATUS_CHOICES, PRICE_FILTER, WEIGHT_FILTER, DISTRICT_CHOICES
from Store.models import BookBank, Product, ProductImages, Review, Store, StoreCertificate, SocialQRCode
from Cart.models import ORDER_STATUS_CHOICES, Order, OrderItem, TransferNotification
from Cart.form import SetOrderStatus
from Members.models import Trader
from lavadurian import settings
from Cart.views import shippingCostCalculate
import random

# Decorator Function


def group_required(*group_names):
    """
    Requires user membership in at least one of the groups passed in.
    Checks is_active and allows superusers to pass regardless of group
    membership.
    """
    def in_group(u):
        return u.is_active and (u.is_superuser or bool(u.groups.filter(name__in=group_names)))

    return user_passes_test(in_group)


@login_required
@group_required("trader")
def storePage(request):
    if request.method == 'POST':
        form = CreateStoreForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/store/manage/')
        else:
            print("Form is not valid !!")
    else:
        form = CreateStoreForm(initial={'owner': request.user})
        form.fields['owner'].widget = forms.HiddenInput()
        form.fields['status'].widget = forms.HiddenInput()

    store_obj = Store.objects.filter(
        owner=request.user).order_by('-date_created')

    for store in store_obj:
        store.status_choice = getModelChoice(store.status, STATUS_CHOICES)

        # get number of products in current store
        store.items_count = Product.objects.filter(store=store).count()

        # get number of review in current store
        store.reviews_count = Review.objects.filter(store=store).count()

    context = {
        'title': 'จัดการร้านค้าของฉัน',
        'subtitle': 'สำหรับการจัดการร้าน ผู้ค้าสามารถสร้างร้านของตัวเองได้มากกว่า 1 ร้าน',
        'form': form,
        'stores': store_obj,
    }

    return render(request, 'store_page.html', context)


@login_required
@group_required("trader")
def storeEdit(request, id):
    store = Store.objects.get(id=id)

    # certificate
    certificate = None
    query_set = StoreCertificate.objects.filter(store=store)
    for query in query_set:
        certificate = query

    if store.owner == request.user:
        if request.method == 'POST':
            form = CreateStoreForm(request.POST, request.FILES, instance=store)

            if certificate != None:
                cer_form = StoreCertificateForm(
                    request.POST, request.FILES, instance=certificate)
            else:
                cer_form = StoreCertificateForm(request.POST, request.FILES)

            if form.is_valid():
                form.save()
                return redirect('/store/manage/'+str(id))
            else:
                print("Form is not valid !!")

            if cer_form.is_valid():
                cer_form.save()
                return redirect('/store/manage/'+str(id))
            else:
                print("Form is not valid !!")
        else:
            form = CreateStoreForm(instance=store)
            form.fields['owner'].widget = forms.HiddenInput()
            form.fields['name'].widget = forms.HiddenInput()
            form.fields['status'].widget = forms.HiddenInput()

            if certificate == None:
                cer_form = StoreCertificateForm(initial={'store': store})
                cer_form.fields['store'].widget = forms.HiddenInput()
            else:
                cer_form = StoreCertificateForm(instance=certificate)
                cer_form.fields['store'].widget = forms.HiddenInput()

            context = {
                'title': store.name,
                'subtitle': store.slogan,
                'form': form,
                'cer_form': cer_form,
                'store': store,
            }

            return render(request, 'store_edit.html', context)
    else:
        return redirect("/")


@login_required
@group_required("trader")
def storeManage(request, id):
    store = Store.objects.get(id=id)
    if store.owner == request.user:
        # Get all products in this store
        products = Product.objects.filter(store=store).order_by('-date_update')
        for product in products:
            product.status_choice = getModelChoice(
                product.status, PRODUCT_STATUS_CHOICES)
            product.grade_choice = getModelChoice(product.grade, GRADE_CHOICES)
            product.gene_choice = getModelChoice(product.gene, GENE_CHOICES)

            # get order items quntity for current product
            product.total_quantity = OrderItem.objects.filter(
                product=product).aggregate(Sum('quantity'))
            if product.total_quantity.get('quantity__sum') == None:
                product.total_quantity['quantity__sum'] = '-'

        # Add book bank form
        bank_form = BankForm(initial={"store": store})
        bank_form.fields['store'].widget = forms.HiddenInput()

        # Get all bookbank of this store
        bookbanks = BookBank.objects.filter(
            store=store).order_by('-date_created')
        for bookbank in bookbanks:
            bookbank.transfer_count = TransferNotification.objects.filter(
                bookbank=bookbank).count()
            bookbank.bank_choice = getModelChoice(bookbank.bank, BANK)
            bookbank.account_type_choice = getModelChoice(
                bookbank.account_type, ACCOUNT_TYPE)

        # Get order and group by status
        order_status = Order.objects.filter(store=store).values(
            'status').annotate(total=Count('status')).order_by('status')
        display_status = []
        for choice in ORDER_STATUS_CHOICES:
            status = {}
            status['status'] = choice[0]
            status['label'] = choice[1]
            status['value'] = 0
            for result in order_status:
                if result['status'] == choice[0]:
                    status['value'] = result['total']
                    break
            display_status.append(status)

        context = {
            'title': store.name,
            'subtitle': store.slogan,
            'store': store,
            'products': products,
            'bank_form': bank_form,
            'bookbanks': bookbanks,
            'status_choice': display_status,
        }
        return render(request, 'store_setting.html', context)
    else:
        return redirect("/")


@login_required
@group_required("trader")
def storeAddBookBank(request):
    if request.method == "POST":
        form = BankForm(request.POST)
        if form.is_valid:
            store_id = request.POST.get('store')
            form.save()
            return redirect("/store/manage/"+str(store_id))


@login_required
@group_required("trader")
def storeDeleteBookBank(request, id):
    bookbank = BookBank.objects.get(id=id)
    if bookbank != None:
        transfer_count = 0
        transfer_count = TransferNotification.objects.filter(
            bookbank=bookbank).count()
        if transfer_count == 0:
            if bookbank.store.owner == request.user:
                store_id = bookbank.store.id
                bookbank.delete()
                return redirect("/store/manage/"+str(store_id))
            else:
                return redirect("/")
        else:
            return redirect("/")
    else:
        return redirect("/")


@login_required
@group_required("trader")
def storeAddProduct(request, id):
    ImageFormSet = modelformset_factory(ProductImages,
                                        form=ProductImageForm, extra=3)

    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES)

        formset = ImageFormSet(request.POST, request.FILES,
                               queryset=ProductImages.objects.none())

        if form.is_valid() and formset.is_valid():
            product = form.save()
            for form in formset.cleaned_data:
                if form.get("image") != None:
                    image = form['image']
                    photo = ProductImages(product=product, image=image)
                    photo.save()

            return redirect('/store/manage/'+str(id))
        else:
            print("Form is not valid !!")
            return redirect('/store/manage/'+str(id))
    else:
        store = Store.objects.get(id=id)
        form = AddProductForm(initial={'store': store})
        form.fields['store'].widget = forms.HiddenInput()

        formset = ImageFormSet(queryset=ProductImages.objects.none())

        if store.owner == request.user:
            context = {
                'title': store.name,
                'subtitle': store.slogan,
                'store': store,
                'form': form,
                'formset': formset,
            }
            return render(request, 'store_add_produdct.html', context)
        else:
            return redirect("/")


@login_required
@group_required("trader")
def storeProductDetail(request, id):
    product = Product.objects.get(id=id)
    if product.store.owner == request.user:
        product.gene_choice = getModelChoice(product.gene, GENE_CHOICES)
        product.status_choice = getModelChoice(
            product.status, PRODUCT_STATUS_CHOICES)
        product.grade_choice = getModelChoice(product.grade, GRADE_CHOICES)

        images = ProductImages.objects.filter(product=product)

        # get order details for current product
        lastest_item_date = ''
        total_values = 0
        total_price = 0
        buyer = []
        items = []

        items = OrderItem.objects.filter(
            product=product).order_by('-date_created')
        if len(items) != 0:
            lastest_item_date = items[0].date_created
            for item in items:
                total_values += item.quantity
                total_price += item.price
                if item.order.owner not in buyer:
                    buyer.append(item.order.owner)

        for image in images:
            image.url = image.image.url

        context = {
            'title': product.store,
            'subtitle': product.store.slogan,
            'product': product,
            'images': images,
            'items': items,
            'buyer': buyer,
            'total_values': total_values,
            'total_price': total_price,
            'lastest_item_date': lastest_item_date,
        }

        return render(request, 'store_product_detail.html', context)
    else:
        return redirect("/")


@login_required
@group_required("trader")
def storeProductEdit(request, id):
    max_img_up = 3

    product = Product.objects.get(id=id)
    images = ProductImages.objects.filter(product=product)

    ImageFormSet = modelformset_factory(ProductImages,
                                        form=ProductImageForm, extra=max_img_up - len(images))

    if product.store.owner == request.user:
        if request.method == 'POST':
            formset = ImageFormSet(request.POST, request.FILES,
                                   queryset=ProductImages.objects.none())

            form = AddProductForm(
                request.POST, request.FILES, instance=product)

            if form.is_valid() and formset.is_valid():
                form.save()
                for form in formset.cleaned_data:
                    if form.get("image") != None:
                        image = form['image']
                        photo = ProductImages(product=product, image=image)
                        photo.save()

            return redirect("/store/manage/"+str(product.store.id))
        else:
            # Check current product has ordered
            item_count = OrderItem.objects.filter(product=product).count()

            form = AddProductForm(instance=product)
            form.fields['store'].widget = forms.HiddenInput()

            if item_count != 0:
                form.fields['grade'].widget = forms.HiddenInput()
                form.fields['gene'].widget = forms.HiddenInput()
                form.fields['price'].widget = forms.HiddenInput()
                form.fields['weight'].widget = forms.HiddenInput()

            formset = ImageFormSet(queryset=ProductImages.objects.none())

            for image in images:
                image.url = image.image.url

            context = {
                'title': product.store,
                'subtitle': product.store.slogan,
                'product': product,
                'item_count': item_count,
                'form': form,
                'formset': formset,
                'images': images,
                'max_img_up': max_img_up,
            }
            return render(request, 'store_product_edit.html', context)
    else:
        return redirect("/")


@login_required
@group_required("trader")
def deleteProduct(request, id):
    product = Product.objects.get(id=id)
    if product.store.owner == request.user:
        store_id = product.store.id
        product.delete()
        return redirect("/store/manage/"+str(store_id))
    else:
        return redirect("/")


@login_required
@group_required("trader")
def deleteProductImage(request, id):
    image = ProductImages.objects.get(id=id)
    if image.product.store.owner == request.user:
        product_id = image.product.id
        image.delete()
        return redirect("/store/product/"+str(product_id)+"/edit/")
    else:
        return redirect("/")


def showCertificate(request, id):
    certificate = None
    default = 'https://res.cloudinary.com/sisaket-rajabhat-university/image/upload/v1587713883/Slide1_r1z78e.jpg'

    queryset = StoreCertificate.objects.filter(store=id)
    for query in queryset:
        certificate = query

    if certificate != None:
        context = {
            'title': 'ใบประกาศของร้าน : '+certificate.store.name,
            'subtitle': certificate.store.slogan,
            'certificate': certificate,
            'default': default,
        }
        return render(request, 'store_certificate.html', context)
    else:
        return redirect("/")

# -------------------------------------------------------------------
# Shopping Section


def thai_time(date):
    tz = pytz.timezone('Asia/Bangkok')
    now1 = datetime.datetime.now(tz)
    month_name = 'x มกราคม กุมภาพันธ์ มีนาคม เมษายน พฤษภาคม มิถุนายน กรกฎาคม สิงหาคม กันยายน ตุลาคม พฤศจิกายน ธันวาคม'.split()[
        now1.month]
    thai_year = now1.year + 543
    time_str = now1.strftime('%H:%M')
    # 30 ตุลาคม 2560 20:45:30
    return "%d %s %d %s" % (now1.day, month_name, thai_year, time_str)


def shoppingPage(request):
    page_title = 'เลือกซื้อทุเรียนออนไลน์'
    filter_price = ''
    filter_weight = ''
    filter_district = ''

    # Dynamic Query
    q_objects = Q()
    q_district = Q()
    gene_objects = Q()

    # Product status must be not equal 3
    q_status = ~Q(status=3)

    for param, vals in request.GET.lists():
        if param == "store":
            for val in vals:
                if val == "":
                    val = 0
                stores = Store.objects.filter(id=val)
                for store in stores:
                    q_objects &= Q(store=store)
        elif param == "weight":
            for val in vals:
                weight = val.split("_")
                q_objects &= Q(weight__gte=weight[0])
                q_objects &= Q(weight__lte=weight[1])
                filter_weight = getModelChoice(val, WEIGHT_FILTER)
        elif param == "price":
            for val in vals:
                price = val.split("_")
                q_objects &= Q(price__gte=price[0])
                q_objects &= Q(price__lte=price[1])
                filter_price = getModelChoice(val, PRICE_FILTER)
        elif param == "grade":
            for val in vals:
                if val == 'normal':
                    q_objects &= Q(grade=1)
                elif val == 'premium':
                    q_objects &= Q(grade=2)
        elif param == "district":
            for val in vals:
                if val != "all":
                    q_district &= Q(store__district=val)
                    filter_district = getModelChoice(
                        int(val), DISTRICT_CHOICES)

        # Gene (optional OR)
        elif param == "gene1":
            for val in vals:
                gene_objects |= Q(gene=1)
        elif param == "gene2":
            for val in vals:
                gene_objects |= Q(gene=2)
        elif param == "gene3":
            for val in vals:
                gene_objects |= Q(gene=3)
        elif param == "gene4":
            for val in vals:
                gene_objects |= Q(gene=4)
        elif param == "gene5":
            for val in vals:
                gene_objects |= Q(gene=5)
        elif param == "gene6":
            for val in vals:
                gene_objects |= Q(gene=6)
        elif param == "gene7":
            for val in vals:
                gene_objects |= Q(gene=7)

        elif param == "status":
            for val in vals:
                if val != "0":
                    q_status &= Q(status=val)

    # Dynamic Query by Using Q Objects
    products = Product.objects.filter(
        q_status & q_objects & gene_objects & q_district).order_by('-date_update')

    for product in products:
        images = ProductImages.objects.filter(
            product=product).order_by('id')[:1]
        # if (len(images) != 0 and product.id > 167):
        if (len(images) != 0):
            product.img_detault = False
            for image in images:
                product.image = image.image.url
        else:
            product.img_detault = True
            product.image = "/assets/img/product-default/default.jpg"

        product.status_choice = getModelChoice(
            product.status, PRODUCT_STATUS_CHOICES)
        product.gene_choice = getModelChoice(product.gene, GENE_CHOICES)
        product.status_choice = getModelChoice(
            product.status, PRODUCT_STATUS_CHOICES)
        product.grade_choice = getModelChoice(product.grade, GRADE_CHOICES)

        product.price_total = int(product.price * product.weight)

    context = {
        'title': page_title,
        'subtitle': thai_time(date.today()),
        'products': products,
        'filter_price': filter_price,
        'filter_weight': filter_weight,
        'filter_district': filter_district,
    }

    # Display only one store
    try:
        if request.GET.get('store') != "":
            review_score = 0
            review_count = 0
            store.product_count = 0
            store.review_rate = [1, 2, 3, 4, 5]
            products = Product.objects.filter(store=store)
            for product in products:
                # get average reviews
                score = Review.objects.filter(
                    product=product).aggregate(Avg('score'))
                if score['score__avg'] != None:
                    review_score += score['score__avg']
                    review_count += 1

                if review_count != 0:
                    store.review_avg = round(review_score / review_count)
                else:
                    store.review_avg = 0

                # count product
                if product.status != 3:
                    store.product_count += 1

            context['store'] = store

            # * Get social qr code for contact
            qrcodes_lt = []
            qrcodes = SocialQRCode.objects.filter(store=store, social=1)
            if len(qrcodes) > 0:
                for qrcode in qrcodes:
                    qrcode.social_name = getModelChoice(
                        qrcode.social, SOCIAL_TYPE)
                    qrcodes_lt.append(qrcode)
            else:
                pass

            qrcodes = SocialQRCode.objects.filter(store=store, social=2)
            if len(qrcodes) > 0:
                for qrcode in qrcodes:
                    qrcode.social_name = getModelChoice(
                        qrcode.social, SOCIAL_TYPE)
                    qrcodes_lt.append(qrcode)
            else:
                qrcode = {
                    'store': store,
                    'social_name': 'Line',
                    'qr_code': '/assets/img/product-default/qrcode_default.png',
                    'default': True,
                }
                qrcodes_lt.append(qrcode)

            context['qr_code'] = qrcodes_lt

    except NameError:
        pass

    return render(request, 'shopping_page.html', context)


'''
Extend home page
Get 4x2 products by random number
'''


def homePageExtended():
    item_show = 12

    product_set1 = []
    product_set2 = []
    product_set3 = []
    products = Product.objects.filter(~Q(status=3) & Q(
        store__status=1)).values_list('id', flat=True)

    if len(products) >= item_show:
        product_set_all = preProcessProduct(
            random.sample(list(products), item_show))
        product_set1 = product_set_all[0:4]
        product_set2 = product_set_all[4:8]
        product_set3 = product_set_all[8:12]
    else:
        product_set_all = preProcessProduct(
            random.sample(list(products), len(products)))
        index_upper = 0
        if len(products) <= 4:
            index_upper = len(products)
        else:
            index_upper = 4
        product_set1 = product_set_all[0:index_upper]
        product_set2 = product_set_all[0:index_upper]
        product_set3 = product_set_all[0:index_upper]

    return product_set1, product_set2, product_set3


def preProcessProduct(products_id_set):
    product_set = []
    for i in products_id_set:
        product = Product.objects.get(id=i)
        images = ProductImages.objects.filter(
            product=product).order_by('id')[:1]
        if (len(images) != 0 and product.id > 167):
            product.img_detault = False
            for image in images:
                product.image = image.image.url
        else:
            product.img_detault = True
            product.image = "/assets/img/product-default/default.jpg"

        product.grade_choice = getModelChoice(product.grade, GRADE_CHOICES)
        product_set.append(product)

    return product_set


def shoppingPageAjax(request):
    # return render(request, 'shopping_page_ajax.html', context)
    return HttpResponse("Hello World")


def shoppingProductView(request, id):
    context = {}

    # * check current product id is exist
    products = Product.objects.filter(id=id)
    for product in products:
        images = ProductImages.objects.filter(product=product)
        trader_q = Trader.objects.filter(account=product.store.owner)
        trader = None
        for query in trader_q:
            trader = query

        product.gene_choice = getModelChoice(product.gene, GENE_CHOICES)
        product.status_choice = getModelChoice(
            product.status, PRODUCT_STATUS_CHOICES)
        product.grade_choice = getModelChoice(product.grade, GRADE_CHOICES)
        product.store.district_choice = getModelChoice(
            product.store.district, DISTRICT_CHOICES)

        # Get review of current product if it exist
        reviews = Review.objects.filter(
            product=product).order_by('-date_review')
        score_total = 0
        score_avg = 0

        for review in reviews:
            review.rate = [1, 2, 3, 4, 5]
            score_total += review.score

        if score_total > 0:
            score_avg = score_total / len(reviews)

        for image in images:
            image.url = image.image.url

        context = {
            'title': 'เลือกซื้อทุเรียนออนไลน์',
            'subtitle': thai_time(date.today()),
            'product': product,
            'trader': trader,
            'images': images,
            'reviews': reviews,
            'score_avg': score_avg,
        }

        # * Get QR Code
        qrcodes = SocialQRCode.objects.filter(store=product.store)
        if len(qrcodes) > 0:
            for qrcode in qrcodes:
                qrcode.social_name = getModelChoice(qrcode.social, SOCIAL_TYPE)

            context['qr_codes'] = qrcodes

    if len(context) != 0:
        return render(request, 'shopping_product_detail.html', context)
    else:
        return redirect("/")


def storeListView(request):
    stores = None
    total_products = 0
    trader_type_1 = 0
    trader_type_2 = 0

    trader_name = Q()
    district = Q()

    if request.GET.get("q") != None:
        trader_name = Q(name__icontains=request.GET.get("q"))

    if request.GET.get("district") != None:
        district = Q(district=request.GET.get("district"))

    """
    * filter and show store in status 1 (opened, ready for sale)
    """
    stores = Store.objects.filter(
        district & trader_name & Q(status=1)).order_by('-date_created')

    stores_list = []

    for store in stores:
        # count store owner type
        trader_q = Trader.objects.filter(account=store.owner)
        if len(trader_q) != 0:
            trader = trader_q[0]
            if trader.trader_type == "เจ้าของสวน":
                trader_type_1 += 1
            else:
                trader_type_2 += 1

        products = Product.objects.filter(store=store)
        store.trader_type = trader.trader_type
        store.product_count = 0
        store.review_rate = [1, 2, 3, 4, 5]
        review_score = 0
        review_count = 0

        for product in products:
            # get average reviews
            score = Review.objects.filter(
                product=product).aggregate(Avg('score'))
            if score['score__avg'] != None:
                review_score += score['score__avg']
                review_count += 1

            if review_count != 0:
                store.review_avg = round(review_score / review_count)
            else:
                store.review_avg = 0

            # count product
            if product.status != 3:
                store.product_count += 1

        # count all product
        total_products += store.product_count

        # group data by type of trader
        if request.GET.get("trader") != None:
            tader_cat = request.GET.get("trader")
            if trader.trader_type == tader_cat:
                stores_list.append(store)
        else:
            stores_list.append(store)

        store.district_choice = getModelChoice(
            store.district, DISTRICT_CHOICES)

    # Group by district
    district_list = []
    district_list.append(Store.objects.filter(
        Q(district=1) & Q(status=1)).count())
    district_list.append(Store.objects.filter(
        Q(district=2) & Q(status=1)).count())
    district_list.append(Store.objects.filter(
        Q(district=3) & Q(status=1)).count())

    context = {
        'title': 'รายชื่อผู้จำหน่ายทุเรียน',
        'subtitle': 'รายชื่อสวนและผู้จำน่ายทุเรียนที่นำสินค้ามาวางขายในตลาดทุเรียนภูเขาไฟออนไลน์',
        'stores': stores_list,
        'total_stores': len(stores),
        'total_products': total_products,
        'trader_type_1': trader_type_1,
        'trader_type_2': trader_type_2,
        'district_list': district_list,
    }
    return render(request, 'store_list_view.html', context)


def storeLocation(request, id):
    context = {}
    return render(request, 'store_location_view.html', context)


@login_required
@group_required("trader")
def stroeSalesCheck(request, id):
    status = 0

    store = Store.objects.get(id=id)

    q_objects = Q()
    q_objects &= Q(store=store)

    # get prameter values
    for param, vals in request.GET.lists():
        if param == "status":
            for val in vals:
                q_objects &= Q(status=val)
                status = val

    # Dynamic query by url parameters
    orders = Order.objects.filter(q_objects).order_by('-date_created')

    for order in orders:
        order.item_count = 0
        order.total_weight = 0
        order.total_price = 0

        items = OrderItem.objects.filter(order=order)

        for item in items:
            order.total_weight += item.weight
            order.total_price += item.price
            order.item_count += 1

        order.status_choice = getModelChoice(
            order.status, ORDER_STATUS_CHOICES)

        # add total price with shipping cost
        order.total_price += order.shipping

        # add total price with box cost
        order.total_price += order.box_1 + order.box_2

    if status != 0:
        status_display = ''
        status_display = getModelChoice(int(status), ORDER_STATUS_CHOICES)
    else:
        status_display = 'แสดงทุกรายการสั่งซื้อ'

    # Get order and group by status
    order_status = Order.objects.filter(store=store).values(
        'status').annotate(total=Count('status')).order_by('status')
    display_status = []
    for choice in ORDER_STATUS_CHOICES:
        status = {}
        status['status'] = choice[0]
        status['label'] = choice[1]
        status['value'] = 0
        for result in order_status:
            if result['status'] == choice[0]:
                status['value'] = result['total']
                break
        display_status.append(status)

    context = {
        'title': store.name,
        'subtitle': store.slogan,
        'store': store,
        'orders': orders,
        'status_display': status_display,
        'status_choice': display_status
    }

    return render(request, 'store_salecheck.html', context)

# Mapping Chice : int to string


def getModelChoice(intValue, choices):
    choice_result = ''
    for choice in choices:
        if choice[0] == intValue:
            choice_result = choice[1]
            break
    return choice_result

# for test email sending


@login_required
def sendMail(request):
    subject = 'Thank you for registering to our site'
    message = 'it  means a world to us'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['phisan.s@sskru.ac.th', ]
    send_mail(subject, message, email_from, recipient_list)

    return redirect("/")


def sendMailStoreApproved(request, store):
    subject = 'ร้านค้าออนไลน์ได้รับการอนุมัติแล้ว'
    message = 'ร้าน '+store.name + \
        " ได้ท่านได้ทำการเปิดไว้บน www.lavadurian.com ได้ผ่านการอนุมัติจากผู้ดูแลแล้ว"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [store.owner.email, ]
    send_mail(subject, message, email_from, recipient_list)
