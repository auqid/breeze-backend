import datetime

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models

# Create your models here.
from django.utils.timezone import utc


class UserManager(BaseUserManager):

    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an phone')

        user = self.model(
            email=email,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_new_user(self, phone_no, password, is_verify, email,
                        full_name, application_id):
        """
        Creates and saves a User with the given email and password.
        """
        if not phone_no:
            raise ValueError('Users must have an phone_no')

        user = self.model(
            phone_no=phone_no,
            is_email_verify=is_verify,
            email=email,
            username=full_name,
            application_id=application_id
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email=email,
            password=password,
        )

        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    phone_no = models.CharField(
        verbose_name='phone_no',
        max_length=20
    )
    username = models.CharField(
        verbose_name='username',
        max_length=100,
    )
    avatar = models.ImageField(
        verbose_name='avatar',
        upload_to='user/avatar/',
        null=True,
        default='/profile_icon.png'
    )
    email = models.CharField(
        verbose_name='email',
        max_length=100,
        unique=True,
    )
    application_id = models.CharField(
        verbose_name='app_id',
        max_length=20,
    )
    is_verify = models.BooleanField(
        verbose_name='is_verify',
        default=False
    )
    country_code = models.CharField(
        max_length=5,
        null=False,
        default='+91'
    )
    added_on = models.DateTimeField(auto_now_add=True, blank=True)
    active = models.BooleanField(default=True)
    # a admin user; non super-user
    is_staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)  # a superuser
    is_email_verify = models.BooleanField(
        verbose_name='is_email_verify',
        default=False
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email & Password are required by default.

    objects = UserManager()

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def verify_email(self, is_verify):
        self.is_email_verify = is_verify
        self.save()
        return is_verify

    def __str__(self):
        return str(self.phone_no)+" "+str(self.username)


class GenerateOTP(models.Model):
    otp = models.IntegerField()
    type = models.CharField(max_length=255, default="register")
    phone_no = models.CharField(max_length=13, null=False)
    country_code = models.CharField(max_length=5)
    attempts = models.IntegerField(default=5)
    global_attempts = models.IntegerField(default=9)
    verify_attempts = models.IntegerField(default=5)
    time_generate_otp = models.DateTimeField(auto_now_add=True, blank=True)

    def get_time_diff(self):
        if self.time_generate_otp:
            now = datetime.datetime.now().utcnow().replace(tzinfo=utc)
            time_difference = now - self.time_generate_otp

            return time_difference.total_seconds()

    def __str__(self):
        return str(self.phone_no)


class ForgotPasswordUser(models.Model):
    application_id = models.CharField(verbose_name='app_id', max_length=20,)
    phone_no_or_email = models.CharField(
        verbose_name='phone_no_or_email', max_length=100, null=True)
    time_generate_otp = models.DateTimeField(auto_now_add=True)

    def get_time_diff(self):
        if self.time_generate_otp:
            now = datetime.datetime.utcnow().replace(tzinfo=utc)
            time_difference = now - self.time_generate_otp

            return time_difference.total_seconds()

    def __str__(self):
        return "{}".format(self.phone_no)


class BlockedPhoneNumber(models.Model):
    phone_no_or_email = models.CharField(max_length=100, null=True)
    reason = models.CharField(max_length=1000, blank=False)

    def __str__(self):
        return str(self.phone_no)


class GenerateOTPEmail(models.Model):
    otp = models.IntegerField()
    type = models.CharField(max_length=255, default="register")
    email = models.CharField(max_length=100, null=False)
    attempts = models.IntegerField(default=5)
    global_attempts = models.IntegerField(default=9)
    verify_attempts = models.IntegerField(default=5)
    time_generate_otp = models.DateTimeField(auto_now_add=True, blank=True)

    def get_time_diff(self):
        if self.time_generate_otp:
            now = datetime.datetime.utcnow().replace(tzinfo=utc)
            time_difference = now - self.time_generate_otp

            return time_difference.total_seconds()

    def __str__(self):
        return str(self.email)
