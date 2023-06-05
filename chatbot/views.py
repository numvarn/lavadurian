from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

# Create your views here.


@api_view(["POST", ])
@permission_classes((AllowAny,))
def webhook(request):
    return Response({'fulfillmentText': 'Hello from the bot world'})
