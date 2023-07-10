from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import SendPasswordResetEmailSerializer, UserChangePasswordSerializer, UserLoginSerializer, UserPasswordResetSerializer, UserProfileSerializer, UserRegistrationSerializer,UserRegistrationEmailSerializer
from django.contrib.auth import authenticate
from .renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.decorators import api_view, permission_classes
# Create your views here.


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



@permission_classes([AllowAny])
class UserRegistrationEmailView(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request,format=None):
        serializer = UserRegistrationEmailSerializer(data= request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response({'msg':' opt sent'},status=status.HTTP_201_CREATED)

class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request,format=None):
        serializer = UserRegistrationSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            user  = serializer.save()
            token = get_tokens_for_user(user)
            return Response({'token':token,'msg':' registration success'},status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request,format=None):
        serializer = UserLoginSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = authenticate(email=email,password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                return Response({'token':token,'msg':' login success'},status=status.HTTP_200_OK)
            return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}\
                ,status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    def get(self,request,format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data,status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
class UserChangePassword(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request,format=None):
        serializer = UserChangePasswordSerializer(data = request.data,\
            context = {
                'user':request.user
            })
        if serializer.is_valid(raise_exception=True):
            return Response({'msg':'Password Changed successfully'},status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request,format=None):
        serializer = SendPasswordResetEmailSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            return Response({'msg':'Password Reset Link Sent Successfully'},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordResetView(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request,uid,token, format=None):
        serializer = UserPasswordResetSerializer(data=request.data, context ={
            'uid':uid,
            'token':token
            }) 
        if serializer.is_valid(raise_exception=True):
            return Response({'msg':'Password Reset successfully'},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)