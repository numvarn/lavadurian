import json
import random
from datetime import date
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Avg, Max, Min, Q, Sum

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    TextSendMessage, FlexSendMessage, BubbleContainer, ImageComponent, URIAction, BoxComponent, TemplateSendMessage, CarouselTemplate, CarouselColumn,
    PostbackAction, MessageAction,
)

from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from News.models import News

from Store.models import (
    Store,
    Product,
    DISTRICT_CHOICES,
    GENE_CHOICES,
    GRADE_CHOICES,
    PRODUCT_STATUS_CHOICES,
)

# Create your views here.
# --
# Channel access token
line_bot_api = LineBotApi(
    '44nraRMP/YnibO5uFL6shJokimaaEYBUNOl/37f+x+ESI3Q1onmCMupjCAKJXbbb7ZYhyBKCJy4mTXElLQtZPhPNh6FNwph/eaiPcgZn3IHWdsNQCoAtcf5Al1obOGIKfqs8C56XewI21RwB1iEvqQdB04t89/1O/w1cDnyilFU=')
# --
# Channel secret
handler = WebhookHandler('323ed2dfb83146a65daa0e97177f07c3')


@api_view(["POST", ])
@permission_classes((AllowAny,))
def webhook(request):
    req = request.data

    intent = req.get('queryResult').get('intent').get('displayName')
    text = req.get('queryResult').get('queryText')

    reply_token = req.get('originalDetectIntentRequest').get(
        'payload').get('data').get('replyToken')

    id = req.get('originalDetectIntentRequest').get(
        'payload').get('data').get('source').get('userId')

    # ชื่อ แสดงของผู้สนทนา
    disname = line_bot_api.get_profile(id).display_name

    # ร้านแนะนำ
    if intent == 'SuggestStore':
        replySuggestStore(reply_token, disname)

    # ตรวจสอบราคา
    elif intent == 'CheckPrice':
        replyPrice(reply_token, disname)

    # ขอข้อมูลสวน
    elif intent == 'GetStoreProfile':
        replyProfile(reply_token, disname, text)

    # ค้นหา สิ้นค้า จากช่วงน้ำหนัก
    elif intent == "GetProductByWeight":
        replyProductByWeight(reply_token, disname, text)

    # ข่าวประชาสัมพันธ์
    elif intent == "News":
        replyNews(reply_token, disname)

    # อื่น ๆ
    else:
        text_message = TextSendMessage(
            text='สวัสดีคุณ {} กรุณารอสักครู่\nเราคือ chatbot จาก www.lavadurian.com'.format(disname))

        line_bot_api.reply_message(reply_token, text_message)

    return Response(status=HTTP_200_OK)

# ---------------------------------------------------------------------


def replyProductByWeight(reply_token, disname, text):
    from decimal import Decimal

    # Prepair Data
    text_lt = text.split(":")
    str = text_lt[1].strip()

    weight_lt = str.split("_")

    start_weight = Decimal(weight_lt[0])
    end_weight = Decimal(weight_lt[1])

    # Crate Query Object
    q_objects = Q(weight__gte=start_weight) & Q(weight__lte=end_weight)
    q_status = ~Q(status=3)

    products = Product.objects.filter(q_objects & q_status)

    if len(products) > 0:
        # สำหรับไว้สุ่มในภายหลัง
        product_list = []
        for product in products:
            if product not in product_list:
                product_list.append(product)

        if len(product_list) > 10:
            product_list_rand = random.sample(product_list, 10)
        else:
            product_list_rand = product_list

        flex_lt = []
        for product in product_list_rand:
            gene_str = getModelChoice(product.gene, GENE_CHOICES)
            flex_str = '''
            {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": "https://www.lavadurian.com/static/assets/info/cover/003.png",
                    "size": "full",
                    "aspectRatio": "4:3",
                    "aspectMode": "cover",
                    "action": {
                    "type": "uri",
                    "uri": "https://www.lavadurian.com"
                    }
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "text": "%s",
                        "weight": "bold",
                        "size": "xl",
                        "wrap": false,
                        "align": "start"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "text",
                            "text": "%s"
                        }
                        ],
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                            {
                                "type": "text",
                                "text": "ราคา (ต่อ/กก.)",
                                "color": "#aaaaaa",
                                "size": "sm",
                                "flex_str": 4
                            },
                            {
                                "type": "text",
                                "text": "%s",
                                "wrap": true,
                                "color": "#666666",
                                "size": "sm",
                                "flex": 2,
                                "align": "end"
                            }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "spacing": "sm",
                            "contents": [
                            {
                                "type": "text",
                                "text": "น้ำหนัก (กก.)",
                                "color": "#aaaaaa",
                                "size": "sm",
                                "flex": 4
                            },
                            {
                                "type": "text",
                                "text": "%s",
                                "wrap": true,
                                "color": "#666666",
                                "size": "sm",
                                "flex": 2,
                                "align": "end"
                            }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                            {
                                "type": "text",
                                "text": "ราคารวม (บาท)",
                                "flex": 4,
                                "size": "sm",
                                "color": "#aaaaaa"
                            },
                            {
                                "type": "text",
                                "text": "%s",
                                "flex": 2,
                                "size": "sm",
                                "color": "#666666",
                                "wrap": true,
                                "align": "end"
                            }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                            {
                                "type": "text",
                                "text": "จำนวน (ลูก)",
                                "flex": 4,
                                "size": "sm",
                                "color": "#aaaaaa"
                            },
                            {
                                "type": "text",
                                "text": "%s",
                                "flex": 2,
                                "size": "sm",
                                "color": "#666666",
                                "align": "end",
                                "wrap": true
                            }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                            {
                                "type": "text",
                                "text": "เกรดทุเรียน",
                                "flex": 4,
                                "size": "sm",
                                "color": "#aaaaaa"
                            },
                            {
                                "type": "text",
                                "text": "%s",
                                "flex": 2,
                                "size": "sm",
                                "color": "#666666",
                                "align": "end",
                                "wrap": true
                            }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                            {
                                "type": "text",
                                "text": "ลักษณะการขาย",
                                "flex": 4,
                                "size": "sm",
                                "color": "#aaaaaa"
                            },
                            {
                                "type": "text",
                                "text": "%s",
                                "flex": 2,
                                "size": "sm",
                                "color": "#666666",
                                "align": "end",
                                "wrap": true
                            }
                            ]
                        }
                        ]
                    }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "button",
                        "action": {
                        "type": "uri",
                        "label": "เลือกซื้อ",
                        "uri": "https://www.lavadurian.com/shopping/product/%s"
                        },
                        "color": "#1DB446"
                    }
                    ]
                }
            }
            ''' % (product.store.name,
                   gene_str, product.price,
                   product.weight,
                   product.price * product.weight,
                   product.values,
                   getModelChoice(product.grade, GRADE_CHOICES),
                   getModelChoice(product.status, PRODUCT_STATUS_CHOICES),
                   product.id)

            flex_lt.append(flex_str)

        flex_close_str = '''
        {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "text",
                    "text": "แสดงข้อมูลอื่น ๆ",
                    "align": "center",
                    "size": "xl",
                    "weight": "bold"
                }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                    "type": "uri",
                    "label": "ไปที่เว็บไซต์",
                    "uri": "https://www.lavadurian.com"
                    },
                    "color": "#1DB446"
                },
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                    "type": "message",
                    "label": "สวนแนะนำ",
                    "text": "สวนแนะนำ"
                    },
                    "color": "#1DB446"
                },
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                    "type": "message",
                    "label": "อื่น ๆ",
                    "text": "อื่น ๆ"
                    },
                    "color": "#1DB446"
                }
                ]
            }
        }
        '''
        flex_lt.append(flex_close_str)

        carousel_str = '''
        {
            "type": "carousel",
            "contents": [
                %s
            ]
        }
        ''' % (",".join(flex_lt))

        carousel = json.loads(carousel_str)
        replyObj = FlexSendMessage(
            alt_text='รายการสินค้าตามที่เลือก', contents=carousel)

        line_bot_api.reply_message(reply_token, replyObj)
    else:
        text_message = TextSendMessage(
            text='น้องทุเรียนไม่พบสินค้าตามช่วงน้ำหนักที่เลือกเลยครับ')

        line_bot_api.reply_message(reply_token, text_message)


# ---------------------------------------------------------------------


def replyProfile(reply_token, disname, text):
    text_lt = text.split(":")
    store_id = text_lt[1].strip()

    store = Store.objects.get(id=int(store_id))

    # count product in store
    product_count = Product.objects.filter(
        Q(store=store) & ~Q(status=3)).count()

    if not store.phone2:
        store.phone2 = '--'

    # district
    district = getModelChoice(store.district, DISTRICT_CHOICES)

    flex_str = """
        {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "text",
                "text": "STORE",
                "weight": "bold",
                "color": "#1DB446",
                "size": "sm"
            },
            {
                "type": "text",
                "text": "%s",
                "weight": "bold",
                "size": "xxl",
                "margin": "md",
                "wrap": true
            },
            {
                "type": "text",
                "text": "โดย %s",
                "size": "xs",
                "color": "#aaaaaa",
                "wrap": true,
                "margin": "md"
            },
            {
                "type": "separator",
                "margin": "xxl"
            },
            {
                "type": "text",
                "text": "%s",
                "margin": "xxl",
                "size": "sm",
                "wrap": true
            },
            {
                "type": "separator",
                "margin": "xl"
            },
            {
                "type": "box",
                "layout": "vertical",
                "margin": "xxl",
                "spacing": "sm",
                "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "text",
                        "text": "โทร.",
                        "size": "sm",
                        "color": "#555555",
                        "flex": 0
                    },
                    {
                        "type": "text",
                        "text": "%s",
                        "size": "sm",
                        "color": "#111111",
                        "align": "end"
                    }
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "text",
                        "text": "โทร.",
                        "size": "sm",
                        "color": "#555555",
                        "flex": 0
                    },
                    {
                        "type": "text",
                        "text": "%s",
                        "size": "sm",
                        "color": "#111111",
                        "align": "end"
                    }
                    ]
                },
                {
                    "type": "separator",
                    "margin": "xxl"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "xxl",
                    "contents": [
                    {
                        "type": "text",
                        "text": "จำนวนสินค้า",
                        "size": "sm",
                        "color": "#555555"
                    },
                    {
                        "type": "text",
                        "text": "%s",
                        "size": "sm",
                        "color": "#111111",
                        "align": "end"
                    }
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                    {
                        "type": "text",
                        "text": "อำเภอ",
                        "size": "sm",
                        "color": "#555555"
                    },
                    {
                        "type": "text",
                        "text": "%s",
                        "size": "sm",
                        "color": "#111111",
                        "align": "end"
                    }
                    ]
                }
                ]
            },
            {
                "type": "box",
                "layout": "horizontal",
                "margin": "xxl",
                "contents": [
                {
                    "type": "text",
                    "text": "STORE ID",
                    "size": "xs",
                    "color": "#aaaaaa",
                    "flex": 0
                },
                {
                    "type": "text",
                    "text": "#%s",
                    "color": "#aaaaaa",
                    "size": "xs",
                    "align": "end"
                }
                ]
            }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "horizontal",
            "contents": [
            {
                "type": "button",
                "action": {
                "type": "uri",
                "label": "ไปที่ร้าน",
                "uri": "https://www.lavadurian.com/shopping/?store=%s"
                },
                "color": "#1DB446"
            },
            {
                "type": "button",
                "action": {
                "type": "message",
                "label": "ร้านอื่น",
                "text": "แนะนำสวน"
                },
                "color": "#1DB446"
            },
            {
                "type": "button",
                "action": {
                "type": "message",
                "label": "เพิ่มเติม",
                "text": "เพิ่มเติม"
                },
                "color": "#1DB446"
            }
            ]
        },
        "styles": {
            "footer": {
            "separator": true
            }
        }
        }
    """ % (store.name, store.owner, store.slogan, store.phone1, store.phone2, product_count, district, store.id, store.id)

    flex = json.loads(flex_str)
    replyObj = FlexSendMessage(alt_text='ร้านแนะนำ', contents=flex)

    line_bot_api.reply_message(reply_token, replyObj)

# ---------------------------------------------------------------------


def replySuggestStore(reply_token, disname):
    # เลือกร้านค้า
    # จากสินค้าที่สถานะพร้อมขาย
    store_list = []
    products = Product.objects.filter(~Q(status=3))
    for product in products:
        if product.store not in store_list:
            store_list.append(product.store)

    # random store in list
    store_list_rand = random.sample(store_list, 5)

    lt = []
    for store in store_list_rand:
        obj = CarouselColumn(
            thumbnail_image_url='https://www.lavadurian.com/static/assets/img/card/01.jpg',
            title=store.name,
            text=store.slogan,
            actions=[
                MessageAction(
                    label='ข้อมูลสวน',
                    text='ผู้ขาย : {}'.format(store.id)
                ),
                URIAction(
                    label='เลือกซื้อจากสวน',
                    uri='https://www.lavadurian.com/shopping/?store={}'.format(
                        store.id)
                )
            ],
        )

        lt.append(obj)

    carousel_template_message = TemplateSendMessage(
        alt_text='ร้านค้าแนะนำ',
        template=CarouselTemplate(
            columns=lt
        )
    )

    line_bot_api.reply_message(
        reply_token, carousel_template_message)

# ---------------------------------------------------------------------


def replyPrice(reply_token, disname):
    store_count = Store.objects.filter(status=1).count()

    # ราคาเกรดธรรมดา
    # ต่ำสุด
    avg = Product.objects.filter(
        ~Q(status=3) & Q(grade=1)).aggregate(Min('price'))
    if avg['price__min'] is not None:
        minPrice_NormalGrade = "{:.0f}".format(avg['price__min'])
    else:
        minPrice_NormalGrade = ""

    # สูงสุด
    avg = Product.objects.filter(
        ~Q(status=3) & Q(grade=1)).aggregate(Max('price'))
    if avg['price__max'] is not None:
        maxPrice_NormalGrade = "{:.0f}".format(avg['price__max'])
    else:
        maxPrice_NormalGrade = ""

    # ราคาเกรดคัด
    # ต่ำสุด
    avg = Product.objects.filter(
        ~Q(status=3) & Q(grade=2)).aggregate(Min('price'))
    if avg['price__min'] is not None:
        minPrice_PremiumGrade = "{:.0f}".format(avg['price__min'])
    else:
        minPrice_PremiumGrade = ""

    # สูงสุด
    avg = Product.objects.filter(
        ~Q(status=3) & Q(grade=2)).aggregate(Max('price'))
    if avg['price__max'] is not None:
        maxPrice_PremiumGrade = "{:.0f}".format(avg['price__max'])
    else:
        maxPrice_PremiumGrade = ""

    # น้ำหนักเฉลี่ยที่วางขาย
    avg = Product.objects.filter(~Q(status=3)).aggregate(Avg('weight'))
    if avg['weight__avg'] is not None:
        avgProduct_Weight = "{:.2f}".format(avg['weight__avg'])
    else:
        avgProduct_Weight = ""

    # Flex Message Template
    flex_str = """
    {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://www.lavadurian.com/static/assets/img/product-default/default.jpg",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "fit",
            "action": {
            "type": "uri",
            "uri": "http://linecorp.com/"
            }
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
            {
                "type": "text",
                "text": "ราคาทุเรียนภูเขาไฟ",
                "weight": "bold",
                "size": "xl"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "text",
                    "text": "ราคาทุเรียนวันที่ %s",
                    "size": "xs",
                    "margin": "md"
                }
                ]
            },
            {
                "type": "box",
                "layout": "vertical",
                "margin": "md",
                "spacing": "sm",
                "contents": [
                {
                    "type": "box",
                    "layout": "baseline",
                    "spacing": "sm",
                    "contents": [
                    {
                        "type": "text",
                        "text": "จำนวนสวน",
                        "color": "#aaaaaa",
                        "size": "xs",
                        "flex": 4
                    },
                    {
                        "type": "text",
                        "text": "%s สวน",
                        "wrap": true,
                        "color": "#666666",
                        "size": "xs",
                        "flex": 5
                    }
                    ],
                    "margin": "xl"
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "spacing": "sm",
                    "contents": [
                    {
                        "type": "text",
                        "text": "เกรดธรรมดา",
                        "color": "#aaaaaa",
                        "size": "xs",
                        "flex": 4
                    },
                    {
                        "type": "text",
                        "text": "ต่ำสุด %s / สูงสุด %s",
                        "wrap": true,
                        "color": "#666666",
                        "size": "xs",
                        "flex": 5
                    }
                    ],
                    "margin": "xl"
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "spacing": "sm",
                    "contents": [
                    {
                        "type": "text",
                        "text": "เกรดคัด",
                        "color": "#aaaaaa",
                        "size": "xs",
                        "flex": 4
                    },
                    {
                        "type": "text",
                        "text": "ต่ำสุด %s / สูงสุด %s",
                        "wrap": true,
                        "color": "#666666",
                        "size": "xs",
                        "flex": 5
                    }
                    ],
                    "margin": "xl"
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "spacing": "sm",
                    "contents": [
                    {
                        "type": "text",
                        "text": "น้ำหนักเฉลี่ย",
                        "color": "#aaaaaa",
                        "size": "xs",
                        "flex": 4
                    },
                    {
                        "type": "text",
                        "text": "%s กก./ลูก",
                        "wrap": true,
                        "color": "#666666",
                        "size": "xs",
                        "flex": 5
                    }
                    ],
                    "margin": "xl"
                }
                ]
            }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "contents": [
            {
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {
                "type": "message",
                "label": "สวนแนะนำ",
                "text": "สวนแนะนำ"
                },
                "color": "#1DB446"
            },
            {
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {
                "type": "message",
                "label": "ข้อมูลอื่น",
                "text": "อื่น ๆ"
                },
                "color": "#1DB446"
            }
            ],
            "flex": 0
        }
    }
    """ % (date.today(), store_count, minPrice_NormalGrade, maxPrice_NormalGrade, minPrice_PremiumGrade, maxPrice_PremiumGrade, avgProduct_Weight)

    flex = json.loads(flex_str)
    replyObj = FlexSendMessage(alt_text='สอบถามราคา', contents=flex)

    line_bot_api.reply_message(reply_token, replyObj)

# ---------------------------------------------------------------------


def replyNews(reply_token, disname):
    flex_lt = []
    news_obj = News.objects.all().order_by("-id")
    for news in news_obj[:5]:
        flex_str = '''
        {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": "%s",
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
                "action": {
                "type": "uri",
                "uri": "https://www.lavadurian.com/news/%s"
                }
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "%s",
                        "weight": "bold",
                        "size": "xl"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "June 17, 2023, 8:09 a.m.",
                                "size": "xs",
                                "color": "#999999"
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                        {
                            "type": "text",
                            "wrap": true,
                            "lineSpacing": "5px",
                            "text": "%s"
                        }
                        ],
                        "margin": "xl"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                    "type": "uri",
                    "label": "รายละเอียด",
                    "uri": "https://linecorp.com"
                    }
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [],
                    "margin": "sm"
                }
                ],
                "flex": 0
            }
        }
        ''' % (news.image.url, news.id, news.title, news.title, )

        flex_lt.append(flex_str)

    carousel_str = '''
        {
            "type": "carousel",
            "contents": [
                %s
            ]
        }
    ''' % (",".join(flex_lt))

    carousel = json.loads(carousel_str)
    replyObj = FlexSendMessage(alt_text='ข่าวประชาสัมพันธ์', contents=carousel)

    line_bot_api.reply_message(reply_token, replyObj)

# ---------------------------------------------------------------------


def getModelChoice(intValue, choices):
    choice_result = ''
    for choice in choices:
        if choice[0] == intValue:
            choice_result = choice[1]
            break
    return choice_result
