from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from core.tasks import load_data
from core.models import BreezeAccount
import urllib
# Create your views here.



@api_view(['GET'])
@permission_classes([AllowAny])
def get_access_code(request):
    acc = BreezeAccount.objects.all().last()
    return Response("https://api.icicidirect.com/apiuser/login?api_key="+urllib.parse.quote_plus(acc.api_key))

@api_view(['GET'])
@permission_classes([AllowAny])
def test(request):
    load_data.delay()
    return Response({"working":"fine"})