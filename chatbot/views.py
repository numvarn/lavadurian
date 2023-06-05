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
    req_dict = json.loads(request.body)
    intent = req_dict["queryResult"]["intent"]["displayName"]

    # intent = req["queryResult"]["intent"]["displayName"]
    text = req_dict['originalDetectIntentRequest']['payload']['data']['message']['text']
    reply_token = req_dict['originalDetectIntentRequest']['payload']['data']['replyToken']
    id = req_dict['originalDetectIntentRequest']['payload']['data']['source']['userId']

    if intent == 'SuggestStore':
        return Response({'fulfillmentText': 'กำลังสืบค้นร้านจาก www.lavadurian.com'})

    elif intent == 'CheckPrice':
        return Response({'fulfillmentText': 'กำลังตรวจสอบราคาจาก www.lavadurian.com'})

    else:
        return Response({'fulfillmentText': ' chatbot จาก www.lavadurian.com'})
