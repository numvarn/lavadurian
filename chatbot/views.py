import json
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    TextSendMessage, FlexSendMessage, BubbleContainer, ImageComponent, URIAction, BoxComponent
)

from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)

from Store.models import Store

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

    if intent == 'SuggestStore':
        text_message = TextSendMessage(
            text='คุณ {} กรุณารอสักครู่\nเรากำลังค้นหาร้านค้าจาก www.lavadurian.com ครับ'.format(disname))

        line_bot_api.reply_message(reply_token, text_message)

    elif intent == 'CheckPrice':
        replyPrice(reply_token, disname)

    else:
        text_message = TextSendMessage(
            text='สวัสดีคุณ {} กรุณารอสักครู่\nเราคือ chatbot จาก www.lavadurian.com'.format(disname))

        line_bot_api.reply_message(reply_token, text_message)

    return Response(status=HTTP_200_OK)


def replyPrice(reply_token, disname):
    store_count = Store.objects.filter(status=1).count()

    text_message_1 = TextSendMessage(
        text='สวัสดีคุณ {} ขอแจ้งราคาทุเรียน\nณ วันที่ {}\nดังนี้ครับ'.format(disname, 'xxx'))

    text_message_2 = TextSendMessage(
        text='จำนวนร้านในตลาดออนไลน์ {}'.format(store_count))

    text_message_3 = TextSendMessage(
        text='ราคาเกรดธรรมดา (บาท/กก.) สูงสุด {} / ต่ำสุด {}'.format(50, 100))

    text_message_4 = TextSendMessage(
        text='ราคาเกรดคัด (บาท/กก.) สูงสุด {} / ต่ำสุด {}'.format(150, 300))

    text_message_5 = TextSendMessage(
        text='น้ำหนักเฉลี่ยที่วางขาย {} กก./ลูก'.format(3.5))

    line_bot_api.reply_message(
        reply_token, [text_message_1, text_message_2, text_message_3, text_message_4, text_message_5])
