# Generated by Django 4.0.2 on 2022-06-10 08:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlockedPhoneNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_no_or_email', models.CharField(max_length=100, null=True)),
                ('reason', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='ForgotPasswordUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application_id', models.CharField(max_length=20, verbose_name='app_id')),
                ('phone_no_or_email', models.CharField(max_length=100, null=True, verbose_name='phone_no_or_email')),
                ('time_generate_otp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='GenerateOTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp', models.IntegerField()),
                ('type', models.CharField(default='register', max_length=255)),
                ('phone_no', models.CharField(max_length=13)),
                ('country_code', models.CharField(max_length=5)),
                ('attempts', models.IntegerField(default=5)),
                ('global_attempts', models.IntegerField(default=9)),
                ('verify_attempts', models.IntegerField(default=5)),
                ('time_generate_otp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='GenerateOTPEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp', models.IntegerField()),
                ('type', models.CharField(default='register', max_length=255)),
                ('email', models.CharField(max_length=100)),
                ('attempts', models.IntegerField(default=5)),
                ('global_attempts', models.IntegerField(default=9)),
                ('verify_attempts', models.IntegerField(default=5)),
                ('time_generate_otp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('phone_no', models.CharField(max_length=20, verbose_name='phone_no')),
                ('username', models.CharField(max_length=100, verbose_name='username')),
                ('avatar', models.ImageField(default='/profile_icon.png', null=True, upload_to='user/avatar/', verbose_name='avatar')),
                ('email', models.CharField(max_length=100, unique=True, verbose_name='email')),
                ('application_id', models.CharField(max_length=20, verbose_name='app_id')),
                ('is_verify', models.BooleanField(default=False, verbose_name='is_verify')),
                ('country_code', models.CharField(default='+91', max_length=5)),
                ('added_on', models.DateTimeField(auto_now_add=True)),
                ('active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('admin', models.BooleanField(default=False)),
                ('is_email_verify', models.BooleanField(default=False, verbose_name='is_email_verify')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
