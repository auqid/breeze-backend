from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from core.tasks import load_data,get_master_data
from core.models import BreezeAccount,Exchanges,Tick
import urllib
# Create your views here.


def item_list(request):
    items = Tick.objects.all().order_by('-date')  
    context = {'items': items[:50]}
    return render(request, 'test.html', context)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_access_code(request):
    acc = BreezeAccount.objects.all().last()
    return Response("https://api.icicidirect.com/apiuser/login?api_key="+urllib.parse.quote_plus(acc.api_key))

@api_view(['GET'])
@permission_classes([AllowAny])
def setup(request):
    get_master_data()
    for exc in Exchanges.objects.all():
        load_data.delay(exc.id)
    return Response({"working":"fine"})