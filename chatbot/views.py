import json
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

    # อื่น ๆ
    else:
        text_message = TextSendMessage(
            text='สวัสดีคุณ {} กรุณารอสักครู่\nเราคือ chatbot จาก www.lavadurian.com'.format(disname))

        line_bot_api.reply_message(reply_token, text_message)

    return Response(status=HTTP_200_OK)

# ---------------------------------------------------------------------


def replySuggestStore(reply_token, disname):
    lt = []

    obj = CarouselColumn(
        thumbnail_image_url='https://www.lavadurian.com/static/assets/img/product-default/default.jpg',
        title='this is menu1',
        text='description1',
        actions=[
            PostbackAction(
                            label='postback1',
                            display_text='postback text1',
                            data='action=buy&itemid=1'
            ),
            MessageAction(
                label='message1',
                text='message text1'
            ),
            URIAction(
                label='uri1',
                uri='https://www.lavadurian.com/shopping/?store=200'
            )
        ],
        default_action=[
            URIAction(
                label="uri1",
                uri='https://www.lavadurian.com/shopping/?store=200')
        ]
    )

    lt.append(obj)

    carousel_template_message = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=lt
        )
    )

    # ตั้งค่าข้อความตอบกลับ Flex Message
    flex_message = FlexSendMessage(
        alt_text='hello',
        contents=BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url='https://s.isanook.com/sp/0/rp/r/w728/ya0xa0m1w0/aHR0cHM6Ly9zLmlzYW5vb2suY29tL3NwLzAvdWQvMjY4LzEzNDAwNTgvcmUoMSkuanBn.jpg',
                size='full',
                aspect_ratio='20:13',
                aspect_mode='cover',
                action=URIAction(
                    uri='http://www.sanook.com', label='label')
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    {
                        "type": "text",
                        "text": "Brown Cafe",
                        "weight": "bold",
                        "size": "xl"
                    },
                ],
            ),
        ),
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

    # text_message_1 = TextSendMessage(
    #     text='สวัสดีคุณ {} ขอแจ้งราคาทุเรียน\nณ วันที่ {}\nดังนี้ครับ'.format(disname, date.today()))

    # text_message_2 = TextSendMessage(
    #     text='จำนวนร้านในตลาดออนไลน์ {} ร้าน'.format(store_count))

    # text_message_3 = TextSendMessage(
    #     text='ราคาเกรดธรรมดา (บาท/กก.) สูงสุด {} / ต่ำสุด {}'.format(minPrice_NormalGrade, maxPrice_NormalGrade))

    # text_message_4 = TextSendMessage(
    #     text='ราคาเกรดคัด (บาท/กก.) สูงสุด {} / ต่ำสุด {}'.format(minPrice_PremiumGrade, maxPrice_PremiumGrade))

    # text_message_5 = TextSendMessage(
    #     text='น้ำหนักเฉลี่ยที่วางขาย {} กก./ลูก'.format(avgProduct_Weight))

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
                "text": "จำนวนสวน",
                "color": "#aaaaaa",
                "size": "sm",
                "flex": 4
              },
              {
                "type": "text",
                "text": "66 สวน",
                "wrap": true,
                "color": "#666666",
                "size": "sm",
                "flex": 5
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
                "text": "เกรดธรรมดา",
                "color": "#aaaaaa",
                "size": "sm",
                "flex": 4
              },
              {
                "type": "text",
                "text": "ต่ำสุด 160 / สูงสุด 200",
                "wrap": true,
                "color": "#666666",
                "size": "sm",
                "flex": 5
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
                "text": "เกรดคัด",
                "color": "#aaaaaa",
                "size": "sm",
                "flex": 4
              },
              {
                "type": "text",
                "text": "ต่ำสุด 160 / สูงสุด 200",
                "wrap": true,
                "color": "#666666",
                "size": "sm",
                "flex": 5
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
                "text": "น้ำหนักเฉลี่ย",
                "color": "#aaaaaa",
                "size": "sm",
                "flex": 4
              },
              {
                "type": "text",
                "text": "2.68 กก./ลูก",
                "wrap": true,
                "color": "#666666",
                "size": "sm",
                "flex": 5
              }
            ]
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
    """

    flex = json.loads(flex_str)
    replyObj = FlexSendMessage(alt_text='Flex Message alt text', contents=flex)

    line_bot_api.reply_message(
        reply_token, replyObj)
