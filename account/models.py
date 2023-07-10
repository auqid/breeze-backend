from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


#custom model
class UserManager(BaseUserManager):
    def create_user(self, email, name,tc,otp, password=None,password2=None):
        """
        Creates and saves a User with the given email, name,
        tc and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            tc=tc,
            otp = otp,
            is_email_verify=True
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email,name,tc,otp, password=None,
    password2=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
            tc=tc,
            otp = otp
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True,
    )
    avatar = models.ImageField(
        verbose_name='avatar',
        upload_to='user/avatar/',
        null=True,
        default='/profile_icon.png'
    )
    name = models.CharField(max_length=200)
    tc = models.BooleanField()
    is_active = models.BooleanField(default=True)
    is_email_verify = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    otp = models.IntegerField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    is_in_session = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','tc']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class UserOtps(models.Model):
    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True,
    )
    otp = models.IntegerField(blank=False,null=False)
    attempts = models.IntegerField(default=5)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return self.email