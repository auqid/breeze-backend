from django.core.management import BaseCommand

from account.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        if User.objects.count() == 0:
            name = 'admin'
            email = 'admin@gmail.com'
            password = 'admin'
            print('Creating account for %s (%s)' % (name, email))
            tc = True
            admin = User.objects.create_superuser(email=email,name=name, otp=12345,password=password,tc=tc)
            admin.is_active = True
            admin.is_admin = True
            admin.save()
        else:
            print('Admin accounts can only be initialized if no Accounts exist')