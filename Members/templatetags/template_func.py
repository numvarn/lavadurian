from django import template
from Cart.models import Cart, CartItem
from Store.models import Product, Store
from django.db.models import Avg, Max, Min, Q, Sum

register = template.Library()

@register.simple_tag(takes_context=True)
def cart_item_count(context): 
    request = context['request']
    session_key = request.session.session_key
    query = []
    count = 0

    query = Cart.objects.filter(session_key=session_key)

    if len(query) != 0:
        cart = query[0]
        count = CartItem.objects.filter(cart=cart).count()
    
    if count > 0:
        return count
    else:
        return ''

@register.simple_tag(takes_context=True)
def cart_item_count_list(context): 
    request = context['request']
    session_key = request.session.session_key
    query = []
    count = 0

    query = Cart.objects.filter(session_key=session_key)

    if len(query) != 0:
        cart = query[0]
        count = CartItem.objects.filter(cart=cart).count()
    
    return count

@register.simple_tag(takes_context=True)
def avgPrice(context):
    avg_w = Product.objects.filter(~Q(status=3)).aggregate(Avg('weight'))
    avg_p = Product.objects.filter(~Q(status=3)).aggregate(Avg('price'))
    if avg_w['weight__avg'] is not None and avg_p['price__avg'] is not None:
        return "{:.2f}".format(avg_w['weight__avg'] * avg_p['price__avg'])
    else:
        return ""

@register.simple_tag(takes_context=True)
def avgProductWeight(context):
    avg = Product.objects.filter(~Q(status=3)).aggregate(Avg('weight'))
    if avg['weight__avg'] is not None:
        return "{:.2f}".format(avg['weight__avg'])
    else:
        return ""

@register.simple_tag(takes_context=True)
def minPriceNormalGrade(context):
    avg = Product.objects.filter(~Q(status=3) & Q(grade=1)).aggregate(Min('price'))
    if avg['price__min'] is not None:
        return "{:.0f}".format(avg['price__min'])
    else:
        return ""

@register.simple_tag(takes_context=True)
def maxPriceNormalGrade(context):
    avg = Product.objects.filter(~Q(status=3) & Q(grade=1)).aggregate(Max('price'))
    if avg['price__max'] is not None:
        return "{:.0f}".format(avg['price__max'])
    else:
        return ""

@register.simple_tag(takes_context=True)
def minPricePremiumGrade(context):
    avg = Product.objects.filter(~Q(status=3) & Q(grade=2)).aggregate(Min('price'))
    if avg['price__min'] is not None:
        return "{:.0f}".format(avg['price__min'])
    else:
        return ""

@register.simple_tag(takes_context=True)
def maxPricePremiumGrade(context):
    avg = Product.objects.filter(~Q(status=3) & Q(grade=2)).aggregate(Max('price'))
    if avg['price__max'] is not None:
        return "{:.0f}".format(avg['price__max'])
    else:
        return ""

@register.simple_tag(takes_context=True)
def avgPriceNormalGrade(context):
    avg = Product.objects.filter(~Q(status=3) & Q(grade=1)).aggregate(Avg('price'))
    if avg['price__avg'] is not None:
        return "{:.2f}".format(avg['price__avg'])
    else:
        return ""

@register.simple_tag(takes_context=True)
def avgPricePremiumGrade(context):
    avg = Product.objects.filter(~Q(status=3) & Q(grade=2)).aggregate(Avg('price'))
    if avg['price__avg'] is not None:
        return "{:.2f}".format(avg['price__avg'])
    else:
        return ""

@register.simple_tag(takes_context=True)
def countNormalGrade(context):
    count = Product.objects.filter(~Q(status=3) & Q(grade=1)).aggregate(Sum('values'))
    return count['values__sum']

@register.simple_tag(takes_context=True)
def countPremiumGrade(context):
    count = Product.objects.filter(~Q(status=3) & Q(grade=2)).aggregate(Sum('values'))
    return count['values__sum']

@register.simple_tag(takes_context=True)
def countStore(context):
    return Store.objects.filter(status=1).count()
