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

from Store.models import (
    Store,
    Product,
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

    # อื่น ๆ
    else:
        text_message = TextSendMessage(
            text='สวัสดีคุณ {} กรุณารอสักครู่\nเราคือ chatbot จาก www.lavadurian.com'.format(disname))

        line_bot_api.reply_message(reply_token, text_message)

    return Response(status=HTTP_200_OK)

# ---------------------------------------------------------------------


def replyProfile(reply_token, disname, text):
    text_lt = text.split(":")
    store_id = text_lt[1].strip()

    store = Store.objects.get(id=int(store_id))

    try:
        if store.phone2 is None:
            store.phone2 = "-"
    # do your thing when user.user_info exists
    except AttributeError:  # Be explicit with catching exceptions.
        store.phone2 = "-"

    # count product in store

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
                "text": "3",
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
                "text": "กันทรลักษ์",
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
            "text": "#200",
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
          "uri": "http://linecorp.com/"
        },
        "color": "#1DB446"
      },
      {
        "type": "button",
        "action": {
          "type": "message",
          "label": "ร้านอื่น ๆ",
          "text": "แนะนำสวน"
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
    """ % (store.name, store.owner, store.slogan, store.phone1, store.phone2)

    flex = json.loads(flex_str)
    replyObj = FlexSendMessage(alt_text='Flex Message alt text', contents=flex)

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
        alt_text='Carousel template',
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
            "aspectMode": "cover",
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
                    "margin": "lg"
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
                    "margin": "md"
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
                    "margin": "md"
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
                    "margin": "md"
                }
                ]
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
                "type": "message",
                "label": "สวนแนะนำ",
                "text": "สวนแนะนำ"
                }
            },
            {
                "type": "button",
                "style": "link",
                "height": "sm",
                "action": {
                "type": "message",
                "label": "อื่น ๆ",
                "text": "อื่น ๆ"
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
    """ % (date.today(), store_count, minPrice_NormalGrade, maxPrice_NormalGrade, minPrice_PremiumGrade, maxPrice_PremiumGrade, avgProduct_Weight)

    flex = json.loads(flex_str)
    replyObj = FlexSendMessage(alt_text='Flex Message alt text', contents=flex)

    line_bot_api.reply_message(reply_token, replyObj)
