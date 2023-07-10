from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from core.tasks import demo
# Create your views here.


@api_view(['GET'])
@permission_classes([AllowAny])
def test(request):
    print("hello world")
    demo.delay()
    return Response({"working":"fine"})