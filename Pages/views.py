from django.shortcuts import render, HttpResponse
from Store.views import homePageExtended

# Create your views here.


def Home(request):
    context = {
        'title': 'ตลาดทุเรียนภูเขาไฟออนไลน์',
        'subtitle': 'ตลาดออนไลน์เพื่อส่งเสริมการซื้อ-ขายทุเรียนภูเขาไฟ จังหวัดศรีสะเกษ',
    }

    # Extended home page
    product_set1, product_set2, product_set3 = homePageExtended()
    context['product_set1'] = product_set1
    context['product_set2'] = product_set2
    context['product_set3'] = product_set3

    return render(request, 'home.html', context)


def DescPage(request):
    context = {
        'title': 'ตลาดทุเรียนภูเขาไฟออนไลน์',
        'subtitle': 'ตลาดออนไลน์เพื่อส่งเสริมการซื้อ-ขายทุเรียนภูเขาไฟ จังหวัดศรีสะเกษ',
    }
    return render(request, 'desc.html', context)


def saleDesc(request):
    context = {
        'title': 'ขั้นตอนการซื้อและขาย',
        'subtitle': 'สรุปขั้นตอนการซื้อและขายทุเรียนผ่านระบบตลาดทุเรียนภูเขาไฟออนไลน์',
    }
    return render(request, 'desc_sales.html', context)


def registerCutter(request):
    context = {}
    return render(request, 'register/cutter.html', context)


def registerPackingHouse(request):
    context = {}
    return render(request, 'register/packing-house.html', context)

# Handle Error


def handler404(request, exception, template_name="404.html"):
    response = render(template_name)
    response.status_code = 404
    return response


def handler401(request, exception, template_name="401.html"):
    response = render(template_name)
    response.status_code = 401
    return response
