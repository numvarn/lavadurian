import json
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

# Create your views here.


@api_view(["POST", ])
@permission_classes((AllowAny,))
def webhook(request):
    req_dict = json.loads(request.body)
    intent = req_dict["queryResult"]["intent"]["displayName"]

    if intent == 'SuggestStore':
        return Response({'fulfillmentText': 'กำลังสืบค้นร้านจาก www.lavadurian.com'})

    elif intent == 'CheckPrice':
        return Response({'fulfillmentText': 'กำลังตรวจสอบราคาจาก www.lavadurian.com'})

    else:
        return Response({'fulfillmentText': ' chatbot จาก www.lavadurian.com'})
