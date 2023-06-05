import json
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

# Create your views here.


@api_view(["POST", ])
@permission_classes((AllowAny,))
def webhook(request):
    req_dict = json.loads(request.data)

    # ตรวนสอบ intent
    intent = req_dict["queryResult"]["intent"]["displayName"]

    if intent == 'SuggestStore':
        return Response({'fulfillmentText': 'กำลังสืบค้นร้านแนะนำจาก www.lavadurian.com'})
    if intent == 'CheckPrice':
        return Response({'fulfillmentText': 'กำลังสืบค้นราคาจาก www.lavadurian.com'})
    else:
        return Response({'fulfillmentText': 'ทุเรียนภูเขาไฟ แชทบอท'})
