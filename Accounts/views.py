import datetime
import hashlib
import random
import threading

import time
from django.contrib.auth import logout, login, authenticate
from django.core.mail import EmailMultiAlternatives, get_connection
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from django.template import loader
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from Accounts.Helper_Utils import RATE_LIMITING_WAIT_TIME
from Accounts.models import User, GenerateOTPEmail, ForgotPasswordUser, GenerateOTP
from Accounts.serializers import LoginSerializer, RegisterSerializer, ForgotPasswordVerifyStep2Serializer, \
    ForgotPasswordVerifyStep1Serializer, ForgotPasswordSerializerEmail, GenerateOTPEmailSerializer, \
    GenerateOTPSerializer
from main import settings


def send_otp_email(data):
    app_name: str = str(settings.app_name)
    message = data['otp'] + " is your verification code for " + app_name + "."
    html_message = get_html_email("Hello User" + ", " + message, "Verification Code: " + data['otp'],
                                  "", "Open App", None)
    email_tuple_list = [("Email Verification Code for your " + app_name + " account!",
                         "", html_message, app_name + "<" + settings.DEFAULT_FROM_EMAIL + ">",
                         [data['email']])]
    emails_tuple = tuple(email_tuple_list)
    mail_res = send_mass_html_mail(emails_tuple)
    # # print response if you want
    response = {'error': False, 'message': 'Sms sent! ' +
                                             str(mail_res), 'token': 'null'}
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_otp_email(request):
    if request.method == "POST":
        serializer = GenerateOTPEmailSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']

            if User.objects.filter(email=email).exists():
                return Response({'error': True, 'message': 'Email already exist with another user',
                                 'token': 'null'})

            random_number_list = [random.randint(0, 9) for p in range(0, 6)]
            otp = ''.join(str(letter) for letter in random_number_list)

            otp_data = {'email': str(email), 'otp': otp}

            if not GenerateOTPEmail.objects.filter(email=email):
                obj = GenerateOTPEmail(email=email, attempts=5, otp=otp)
                obj.save()

            obj = GenerateOTPEmail.objects.get(email=email)
            obj.attempts = obj.attempts - 1
            obj.save()

            if obj.attempts <= 0:
                if obj.get_time_diff() < RATE_LIMITING_WAIT_TIME:
                    return Response({'error': True,
                                     'message': 'Too many tries, please wait {0} seconds'
                                    .format(RATE_LIMITING_WAIT_TIME - int(obj.get_time_diff())),
                                     'token': 'null'})
                obj.time_generate_otp = datetime.datetime.now()
                obj.attempts = 5
                obj.save()
                print('attempts set to 5 -> ', obj.attempts)

            obj.otp = otp
            obj.save()
            res = send_otp_email(otp_data)
            return Response(res)

        return Response({'error': True, 'message': 'Data is not valid!', 'token': 'null'})


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_email(request):
    serializer = ForgotPasswordSerializerEmail(data=request.data)
    if serializer.is_valid():
        user = User.objects.get(email=serializer.validated_data['username'])
        email = user.email

        # create record in forgot password table
        random_number_list = [random.randint(0, 9) for p in range(0, 6)]
        otp = ''.join(str(letter) for letter in random_number_list)

        otp_data = {'email': str(email), 'otp': otp}

        if not GenerateOTPEmail.objects.filter(email=email, type="forget"):
            obj = GenerateOTPEmail(
                email=email, type="forget", attempts=5, otp=otp)
            obj.save()

        obj = GenerateOTPEmail.objects.get(email=email, type="forget")
        obj.attempts = obj.attempts - 1
        obj.save()

        # send otp to mobile number -> check rate limiting
        if obj.attempts <= 0:
            if obj.get_time_diff() < RATE_LIMITING_WAIT_TIME:
                return Response({'error': True,
                                 'message': 'Too many tries, please wait {0} seconds'
                                .format(RATE_LIMITING_WAIT_TIME - int(obj.get_time_diff())),
                                 'token': 'null'})

            obj.time_generate_otp = datetime.datetime.now()
            obj.attempts = 5
            obj.save()
            print('attempts set to 5 -> ', obj.attempts)

        obj.otp = otp
        obj.save()

        return Response(send_otp_email(otp_data))
    return HttpResponse(serializer.errors)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_verify_otp(request):
    serializer = ForgotPasswordVerifyStep1Serializer(data=request.data)

    if serializer.is_valid():
        user_otp = serializer.validated_data['otp']
        user_username = serializer.validated_data['username']
        # user_password = serializer.validated_data['new_password']
        user_application_id = serializer.validated_data['application_id']

        # if len(user_password) < 6:
        #     return Response({'error': True,
        #                      'message': 'Password too short!!! Try password with more than 5 characters'})

        server_otps = GenerateOTP.objects.filter(
            phone_no=user_username, type="forget").order_by('-id')
        if server_otps.count() == 0:
            return Response({'error': True, 'message': 'No record found!'})

        # verify otp api view
        server_otp = server_otps[0]
        if server_otp.otp != user_otp:
            return Response({'error': True, 'message': 'OTP is not valid!'})

        forgot_password_object = ForgotPasswordUser(
            application_id=user_application_id, phone_no_or_email=user_username)
        forgot_password_object.save()

        server_otps.delete()

        return Response({'error': False, 'message': 'OTP is valid, send new password!'})
    else:
        return Response({'error': True, 'message': '{}'.format(serializer.errors)})


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_verify_otp_email(request):
    serializer = ForgotPasswordVerifyStep1Serializer(data=request.data)

    if serializer.is_valid():
        user_otp = serializer.validated_data['otp']
        user_username = serializer.validated_data['username']
        # user_password = serializer.validated_data['new_password']
        user_application_id = serializer.validated_data['application_id']

        # if len(user_password) < 6:
        #     return Response({'error': True,
        #                      'message': 'Password too short!!! Try password with more than 5 characters'})

        server_otps = GenerateOTPEmail.objects.filter(
            email=user_username, type="forget").order_by('-id')
        if server_otps.count() == 0:
            return Response({'error': True, 'message': 'No record found!'})

        # verify otp api view
        server_otp = server_otps[0]
        if server_otp.otp != user_otp:
            return Response({'error': True, 'message': 'OTP is not valid!'})

        forgot_password_object = ForgotPasswordUser(
            application_id=user_application_id, phone_no_or_email=user_username)
        forgot_password_object.save()

        server_otps.delete()

        return Response({'error': False, 'message': 'OTP is valid, send new password!'})
    else:
        return Response({'error': True, 'message': '{}'.format(serializer.errors)})


# delete record and reset password given by user
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_reset_password(request):
    serializer = ForgotPasswordVerifyStep2Serializer(data=request.data)

    if serializer.is_valid():
        ForgetPassObjs = ForgotPasswordUser.objects.filter(application_id=serializer.validated_data['application_id'],
                                                           phone_no_or_email=serializer.validated_data[
                                                               'username']).order_by(
            '-id')
        if ForgetPassObjs.count() == 0:
            return Response({'error': True, 'message': 'No record found!'})

        object_forgot_password_user = ForgetPassObjs[0]

        if object_forgot_password_user.get_time_diff() > 600:
            object_forgot_password_user.delete()
            return Response({'error': True, 'message': 'New password submitted late! Try Again'})

        user_main = User.objects.get(
            phone_no=serializer.validated_data['username'])
        user_main.set_password(serializer.validated_data['new_password'])
        user_main.save()

        ForgetPassObjs.delete()

        return Response({'error': False, 'message': 'New Password set successfully!!!'})
    else:
        return Response({'error': True, 'message': '{}'.format(serializer.errors)})


# delete record and reset password given by user
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_reset_password_email(request):
    serializer = ForgotPasswordVerifyStep2Serializer(data=request.data)

    if serializer.is_valid():
        ForgetPassObjs = ForgotPasswordUser.objects.filter(application_id=serializer.validated_data['application_id'],
                                                           phone_no_or_email=serializer.validated_data[
                                                               'username']).order_by(
            '-id')
        if ForgetPassObjs.count() == 0:
            return Response({'error': True, 'message': 'No record found!'})

        object_forgot_password_user = ForgetPassObjs[0]

        if object_forgot_password_user.get_time_diff() > 600:
            object_forgot_password_user.delete()
            return Response({'error': True, 'message': 'New password submitted late! Try Again'})

        user_main = User.objects.get(
            email=serializer.validated_data['username'])
        user_main.set_password(serializer.validated_data['new_password'])
        user_main.save()

        ForgetPassObjs.delete()

        return Response({'error': False, 'message': 'New Password set successfully!!!'})
    else:
        return Response({'error': True, 'message': '{}'.format(serializer.errors)})


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    if request.method == "POST":
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            if User.objects.filter(email=serializer.validated_data['email_id']).exists():
                return Response({'error': True, 'message': 'email id already exist', 'token': 'null'})

            # if User.objects.filter(username=serializer.validated_data['uname']).exists():
            #    return Response({'error': True, 'message': 'username already taken', 'token': 'null'})

            # ## CONDITION FOR ONE ACCOUNT ON ONE DEVICE ONLY  ##
            # if User.objects.filter(application_id=serializer.validated_data['application_id']).exists():
            #     return Response({'error': True, 'message': 'username already exist', 'token': 'null'})

            # if User.objects.filter(phone_no=serializer.validated_data['phone_no']).exists():
            #     return Response({'error': True, 'message': 'Phone number already exist with another user',
            #                      'token': 'null'})

            if not GenerateOTPEmail.objects.filter(email=serializer.validated_data['email_id']).exists():
                return Response({'error': True,
                                 'message': 'We don\'t have any record with the number',
                                 'token': 'null'})

            otp_object = GenerateOTPEmail.objects.get(
                email=serializer.validated_data['email_id'])
            otp_object.verify_attempts = otp_object.verify_attempts - 1
            print('verify_attempt', otp_object.verify_attempts, otp_object.email)
            otp_object.save()

            if otp_object.verify_attempts <= 0:
                if otp_object.get_time_diff() < RATE_LIMITING_WAIT_TIME:
                    return Response({'error': True,
                                     'message': 'Too many tries!!!, please wait {0} seconds'
                                    .format(RATE_LIMITING_WAIT_TIME - int(otp_object.get_time_diff())),
                                     'token': 'null'})
                otp_object.delete()
                return Response({'error': True,
                                 'message': 'Too many attempts!!!, Please try with new otp',
                                 'token': 'null'})
            stored_otp = otp_object.otp

            if stored_otp != serializer.validated_data['otp']:
                return Response({'error': True, 'message': 'OTP does not matched',
                                 'token': 'null'})
            user_account = User.objects.create_new_user(is_verify=True,
                                                        phone_no=serializer.validated_data['phone_no'],
                                                        email=serializer.validated_data['email_id'],
                                                        full_name=serializer.validated_data['uname'],
                                                        password=serializer.validated_data['password'],
                                                        application_id=serializer.validated_data['application_id'],
                                                    )

            user_account.save()

            # update1
            token = Token.objects.create(user=user_account)

            firebase_token = ""

            # deleting the record from generate otp
            otp_object.delete()
            try:
                send_verification_email_reg(user_account.email)
            except Exception as e:
                print(str(e))

            data = {'error': False,
                    'message': 'user registration successful',
                    'id': user_account.id,
                    'token': token.key,
                    'username': user_account.username,
                    'email': user_account.email,
                    'phone_no': user_account.phone_no,
                    'application_id': user_account.application_id,
                    'country_code': user_account.country_code,
                    'created_at': user_account.added_on,
                    'is_email_verify': str(user_account.is_email_verify),
                    'is_author': str(user_account.is_staff),
                    'is_admin': user_account.admin,
                    'avatar': user_account.file.url,
                    }

            print(data)
            return Response(data)
        else:
            return Response({'error': True, 'message': serializer.errors, 'token': 'null'})
    return Response({'error': True, 'message': 'request type was invalid!!!'})


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    if request.method == 'POST':
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user_account = authenticate(
                request, email=username, password=password)

            # Wrong credentials condition
            if not user_account:
                return Response({'error': True,
                                 'message': 'Please check your credentials!',
                                 'token': 'null'})

            login(request, user_account)

            # Creating new authentication token process
            if Token.objects.filter(user=user_account).exists():
                token = Token.objects.get(user=user_account)
                token.delete()
            token = Token.objects.create(user=user_account)

            # Creating new firebase token process

            user_account.application_id = serializer.validated_data['application_id']
            user_account.save()
            firebase_token = ""

            print("user_account.id", user_account.id)

            if not user_account.is_email_verify:
                return Response({'error': True, 'message': 'Account not verified!', 'token': 'null'})

            is_author = user_account.is_staff
            data = {'error': False,
                    'message': 'user login successful',
                    'token': token.key,
                    'id': user_account.id,
                    'username': user_account.username,
                    'email': user_account.email,
                    'phone_no': user_account.phone_no,
                    'application_id': user_account.application_id,
                    'country_code': user_account.country_code,
                    'created_at': user_account.added_on,
                    'is_admin': user_account.admin,
                    'is_email_verify': str(user_account.is_email_verify),
                    }
            return Response(data)
        else:
            return Response({'error': True, 'message': 'Please provide valid data ! {}'.format(serializer.errors),
                             'token': 'null'})
    else:
        return Response({'error': True, 'message': 'Please provide valid data!', 'token': 'null'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    if request.method == 'POST':
        token = request.user.auth_token
        if Token.objects.filter(key=token).exists():
            token = Token.objects.get(key=token)
            token.delete()
            logout(request)

            return Response({'error': False, 'message': 'You\'re successfully logged out!', 'token': 'null'})
        else:
            return Response({'error': True, 'message': 'You are already logged out!', 'token': 'null'})

    return Response({'error': True, 'message': 'Post method required!', 'token': 'null'})


@api_view(['POST'])
@permission_classes([AllowAny])
def send_verification_email(request):
    email = request.POST.get("email_id")
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        if not user.is_email_verify:
            random_number_list = [random.randint(0, 9) for p in range(0, 6)]
            otp = ''.join(str(letter) for letter in random_number_list)
            if not GenerateOTPEmail.objects.filter(email=email):
                obj = GenerateOTPEmail(email=email, attempts=5, otp=otp)
                obj.save()

            obj = GenerateOTPEmail.objects.get(email=email)
            obj.attempts = obj.attempts - 1
            obj.save()

            if obj.attempts <= 0:
                if obj.get_time_diff() < RATE_LIMITING_WAIT_TIME:
                    return Response({'error': True,
                                     'message': 'Too many tries, please wait {0} seconds'
                                    .format(RATE_LIMITING_WAIT_TIME - int(obj.get_time_diff())),
                                     'token': 'null'})
                obj.time_generate_otp = datetime.datetime.now()
                obj.attempts = 5
                obj.save()
                print('attempts set to 5 -> ', obj.attempts)

            obj.otp = otp
            obj.save()
            verification_url = settings.BASE_URL + 'account/verify_email/?email=' + email + \
                               '&otp=' + otp + '&hash=' + \
                               hashlib.sha1(str(email + otp + 'lawcsaltemail')
                                            .encode('utf-8')).hexdigest()
            mail_res = send_email(user_object_list=[user, ], subject="Email Verification",
                                  body="Hey " + user.username + ", You are almost ready to enjoy learning. Simply "
                                                                "click the below black button to verify email! ",
                                  app_url=verification_url,
                                  book_name="",
                                  button_name="Verify Email", is_verification=True)
            if mail_res != 0:
                return Response({'error': False,
                                 'message': 'Please check your inbox, we have sent you the email',
                                 'number': mail_res})
            else:
                return Response({'error': True,
                                 'message': 'Please try again later, Something went wrong!',
                                 'number': mail_res})
        else:
            return Response({'error': True,
                             'message': 'Your email is already Verified',
                             'number': 0})
    else:
        return Response({'error': True,
                         'message': 'Please try again later, Something went wrong!',
                         'number': 0})


def verify_email(request):
    if request.method == 'GET':
        email = request.GET.get('email')
        otp = request.GET.get('otp')
        hash_request = request.GET.get('hash')
        hash_server = hashlib.sha1(
            str(email + otp + 'lawcsaltemail').encode('utf-8')).hexdigest()

        if hash_server == hash_request:
            user = User.objects.get(email=email)
            if not GenerateOTPEmail.objects.filter(email=email).exists():
                return Response({'error': True,
                                 'message': 'We don\'t have any record with the number',
                                 'token': 'null'})

            otp_object = GenerateOTPEmail.objects.get(email=email)
            otp_object.verify_attempts = otp_object.verify_attempts - 1
            otp_object.save()
            stored_otp = otp_object.otp
            if stored_otp == int(otp):
                otp_object.delete()
                user.verify_email(is_verify=True)
                return render(request, 'authentication/success_verification.html',
                              {'msg': 'Your email successfully verified. Please login!',
                               'url': settings.BASE_URL + '/'})
            else:
                return render(request, 'authentication/success_verification.html',
                              {'msg': 'Your email not verified, link expired . Please try again!',
                               'url': settings.BASE_URL + '/'})
        else:
            return render(request, 'authentication/success_verification.html',
                          {'msg': 'Your email not verified, link expired . Please try again!',
                           'url': settings.BASE_URL + '/'})


def send_verification_email_reg(email):
    email = email
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        return send_email(user_object_list=[user, ], subject="Thanks for registering",
                          body="Hey " + user.username +
                               ", Thank you for registering with us. You are ready to enjoy "
                               "unlimited learning. If you want to unsubscribe for "
                               "email notifications from us. Please contact us at "
                               "contact@geniobits.com",
                          app_url=None,
                          book_name="",
                          button_name="Open app", is_verification=True)
    else:
        return Response("We have no such user!")


def get_html_email(body, subject, course_name, button_name, app_url):
    facebook_url = settings.facebook_url
    twitter_url = settings.twitter_url
    instagram_url = settings.instagram_url
    linkdln_url = settings.linkdln_url
    email = settings.email
    address = settings.address
    app_name = settings.app_name
    if app_url is None:
        app_url = settings.app_url
    html_message = loader.render_to_string(
        'authentication/email.html',
        {
            'body': body,
            'facebook_url': facebook_url,
            'twitter_url': twitter_url,
            'instagram_url': instagram_url,
            'linkdln_url': linkdln_url,
            'email': email,
            'address': address,
            'app_url': app_url,
            'course_name': course_name,
            'button_name': button_name,
            'subject': subject,
            'app_name': app_name
        }
    )
    return html_message


def send_email(user_object_list, subject, body, book_name, button_name, app_url, is_verification=False):
    html_message = get_html_email(
        body, subject, book_name, button_name, app_url)
    if settings.email_enable:
        EmailThread(subject, html_message, settings.app_name, user_object_list, body,
                    is_verification).start()
    return "send email tread started"


def send_mass_html_mail(datatuple, fail_silently=False, user=None, password=None,
                        connection=None):
    """
    Given a datatuple of (subject, text_content, html_content, from_email,
    recipient_list), sends each message to each recipient list. Returns the
    number of emails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    """
    connection = connection or get_connection(
        username=user, password=password, fail_silently=fail_silently)
    messages = []
    for subject, text, html, from_email, recipient in datatuple:
        message = EmailMultiAlternatives(subject, text, from_email, recipient)
        message.attach_alternative(html, 'text/html')
        messages.append(message)
    return connection.send_messages(messages)


class EmailThread(threading.Thread):
    def __init__(self, subject, html_message, app_name, user_object_list, body, is_verification):
        self.subject = subject
        self.app_name = app_name
        self.html_message = html_message
        self.user_object_list = user_object_list
        self.body = body
        self.is_verification = is_verification
        threading.Thread.__init__(self)

    def run(self):
        email_tuple_list = []
        for user in self.user_object_list:
            if user.is_email_verify or self.is_verification:
                email_tuple_list.append(
                    (self.subject, '', self.html_message, self.app_name + "<" + settings.DEFAULT_FROM_EMAIL + ">",
                     [user.email]))
        emails_tuple = tuple(email_tuple_list)
        res = send_mass_html_mail(emails_tuple)
        try:
            historyObjList = []
            for user in self.user_object_list:
                try:
                    log_detail = {
                        'subject': self.subject,
                        'user': user.phone_no,
                        'body': self.body,
                        # 'history_type': history_types.EMAIL,
                        'result': res,
                        'timestamp': time.time()
                    }
                    historyObjList.append(log_detail)
                except Exception as e:
                    print("error in course_video" + str(e))
            # TODO add in history notification
        except Exception as e:
            print("error in course_video" + str(e))


def send_error_email(data):
    app_name: str = 'Trading Automation'
    message = 'Error at ' + datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    html_message= f'''
    <pre>
Dear Client,

I hope this email finds you well. I am writing to inform you that an error message was encountered while attempting to complete the task you assigned us. The error message reads as follows: {data['message']}.

Error ID: {data['id']}
Traceback: 
{data['tb']}

If you have any questions or concerns regarding this issue, please feel free to reach out to us. We appreciate your patience and understanding in this matter.

Best regards,
GENIOBITS PRIVATE LIMITED

    '''
    email_tuple_list = [(app_name + ":" + message ,
                         "", html_message, app_name + "<" + settings.DEFAULT_FROM_EMAIL + ">",
                         ['manish.nathani@gmail.com', 'ravidp111@gmail.com'])]
    # email_tuple_list = [(app_name + ":" + message ,
    #                      "", html_message, app_name + "<" + settings.DEFAULT_FROM_EMAIL + ">",
    #                      ['anujanilmittal@gmail.com'])]
    emails_tuple = tuple(email_tuple_list)
    mail_res = send_mass_html_mail(emails_tuple)
    # # print response if you want
    response = {'error': False, 'message': 'Email Sent! ' + str(mail_res)}
    return response

