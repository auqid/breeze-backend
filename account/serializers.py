from ast import Pass
from dataclasses import field
import imp
from unittest.util import _MAX_LENGTH
from xml.dom import ValidationErr
from rest_framework import serializers
import random
import datetime
import pytz
from account.utils import Util
from .models import User,UserOtps
from django.utils.encoding import smart_str,force_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from main.settings import BASE_DIR,MAIN_URL_2


class UserRegistrationEmailSerializer(serializers.ModelSerializer):
    
    email = serializers.EmailField(max_length = 255)
    class Meta:
        model = UserOtps
        fields = ['email']
    
    def validate(self, attrs):
        email = attrs.get('email')
        query_1 = User.objects.filter(email = attrs.get('email'))
        if query_1.exists():
            raise serializers.ValidationError("User Already Exists!")
        
        query_2 = UserOtps.objects.filter(email = attrs.get('email'))
        if query_2.exists():
            query_2 = query_2.last()
            if query_2.attempts == 0:
                query_2.delete()
            if pytz.UTC.localize(datetime.datetime.now()) - query_2.created_at > datetime.timedelta(minutes=5):
                query_2.delete()
            else:
                raise serializers.ValidationError("OTP Already Sent")
        return attrs
    
    def create(self, validated_data):
        otp = ""
        for i in range(6):
            otp += str(random.randint(0, 9))
        otp = int(otp)
        subject = 'Email OTP'
        to = validated_data.get('email')
        path_to_html =str(BASE_DIR)+"/home/templates/email_otp.html"
        Util.send_html_email(subject,to,path_to_html,otp)
        return UserOtps.objects.create(email=validated_data.get('email'),otp=otp)

class UserRegistrationSerializer(serializers.ModelSerializer):
    
    password2 = serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model = User
        fields = ['email','name','password','password2','tc','otp']
        extra_kwargs = {
            'password':{'write_only':True}
        }
    
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        otp = attrs.get('otp')
        email = attrs.get('email')

        otp_query = UserOtps.objects.filter(email=email)
        if not otp_query.exists():
            raise serializers.ValidationError("OTP for email doesn't exsist.")
        else:
            otp_obj = otp_query.last()
            if pytz.UTC.localize(datetime.datetime.now()) - otp_obj.created_at > datetime.timedelta(minutes=5):
                otp_query.delete()
                raise serializers.ValidationError("OTP expired!!Please redo the registration process.")
            
            if otp_obj.otp != otp:
                if otp_obj.attempts == 1:
                    otp_query.delete()
                    raise serializers.ValidationError("Too many wrong attemps!!Please redo the registration process.")
                otp_obj.attempts -=1
                otp_obj.save()
                raise serializers.ValidationError(f'Incorrect OTP,{otp_obj.attempts} Attempts Remaining')
            else:
                otp_query.delete()
            
        if password != password2:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self,validate_data):
        return User.objects.create_user(**validate_data)

class UserLoginSerializer(serializers.ModelSerializer):
    email  =serializers.EmailField(max_length = 255)
    class Meta:
        model = User
        fields = ['email','password']

class UserProfileSerializer(serializers.ModelSerializer):
    @staticmethod
    def get_avatar(obj):
        try:
            return MAIN_URL_2+obj.avatar.url
        except:
            return None
        
    avatar = serializers.SerializerMethodField('get_avatar')
    class Meta:
        model = User
        fields = ['id','email','name','avatar','is_admin','is_teacher','is_in_session']

class UserChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=255,style = {
        'input_type':'password'},write_only = True)
    password2 = serializers.CharField(max_length=255,style = {
        'input_type':'password'},write_only = True)
    class Meta:
        model = User
        fields = ['password','password2']
    
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')
        if password != password2:
            raise serializers.ValidationError("Passwords don't match")
        user.set_password(password)
        user.save()
        return attrs

class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        fields = ['email']
    
    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user =  User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            #print('Encoded UID ',uid)
            token = PasswordResetTokenGenerator().make_token(user)
            #print('Password token', token)
            link = 'https://naveedkhan1998.github.io/user-auth-react/#/api/user/reset/'+uid+'/'+token+'/'
            ##print('Link reset',link)
            #body = 'Click Following Link to reset your password '+link
            #data = {
            #    'subject':'Password Reset link',
            #    'body':body,
            #    'to_email':user.email
            #}
            #Util.send_email(data)
            subject = 'Reset LINK'
            to = user.email
            #path_to_html = STATIC_ROOT+"templates/email_otp.html"
            path_to_html =str(BASE_DIR)+"/home/templates/password_reset.html"
            Util.send_html_email(subject,to,path_to_html,link)
            return attrs
        raise serializers.ValidationError('You are not registered user.')

class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255,style = {
        'input_type':'password'},write_only = True)
    password2 = serializers.CharField(max_length=255,style = {
        'input_type':'password'},write_only = True)
    class Meta:
        fields = ['password','password2']
    
    def validate(self, attrs):
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')
            if password != password2:
                raise serializers.ValidationError("Passwords don't match")
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user,token):
                raise serializers.ValidationError("Token is not Valid or Expired")
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user,token)
            raise serializers.ValidationError("Token is not Valid or Expired")
