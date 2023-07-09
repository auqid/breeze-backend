from django.utils import timezone
from rest_framework import serializers

from .models import User, GenerateOTP, GenerateOTPEmail


class UserSerializer(serializers.ModelSerializer):
    @staticmethod
    def get_user_avatar_url(obj):
        try:
            return obj.file.url
        except:
            return None

    @staticmethod
    def get_created_at(obj):
        date_time = timezone.localtime(obj.added_on)
        return date_time.strftime("%d %b, %Y %I:%M %p")

    created_at = serializers.SerializerMethodField('get_created_at')
    avatar = serializers.SerializerMethodField('get_user_avatar_url')

    class Meta:
        model = User
        fields = ['id',
                  'username',
                  'email',
                  'phone_no',
                  'country_code',
                  'created_at',
                  'avatar', 'is_email_verify', 'active']


class GenerateOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerateOTP
        fields = ['phone_no', 'country_code']


class GenerateOTPEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerateOTPEmail
        fields = ['email']


class RegisterSerializer(serializers.ModelSerializer):
    otp = serializers.IntegerField()
    email_id = serializers.EmailField()
    uname = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)

    class Meta:
        model = User
        fields = ['phone_no', 'application_id',
                  'otp', 'email_id', 'uname', 'password']


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'application_id']


class ForgotPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'application_id']


class ForgotPasswordSerializerEmail(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'application_id']


class ForgotPasswordVerifyStep1Serializer(serializers.ModelSerializer):
    otp = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['otp', 'username', 'application_id']


class ForgotPasswordVerifyStep2Serializer(serializers.ModelSerializer):
    otp = serializers.IntegerField()
    new_password = serializers.CharField(
        max_length=255, allow_null=False, allow_blank=False)

    class Meta:
        model = User
        fields = ['otp', 'username', 'application_id', 'new_password']


