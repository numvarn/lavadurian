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

    disname = line_bot_api.get_profile(id).display_name

    if intent == 'SuggestStore':
        return Response({'fulfillmentText': 'กำลังสืบค้นร้านจาก www.lavadurian.com '+str(disname)})

    elif intent == 'CheckPrice':
        return Response({'fulfillmentText': 'กำลังตรวจสอบราคาจาก www.lavadurian.com'})

    else:
        return Response({'fulfillmentText': ' chatbot จาก www.lavadurian.com'})
