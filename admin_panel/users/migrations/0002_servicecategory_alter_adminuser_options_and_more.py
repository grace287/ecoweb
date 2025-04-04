# Generated by Django 5.1.6 on 2025-03-05 03:41

import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_code', models.CharField(max_length=20, unique=True, verbose_name='카테고리 코드')),
                ('name', models.CharField(max_length=255, verbose_name='분야')),
                ('description', models.TextField(blank=True, null=True, verbose_name='설명')),
            ],
            options={
                'verbose_name': '서비스 카테고리',
                'verbose_name_plural': '서비스 카테고리 목록',
            },
        ),
        migrations.AlterModelOptions(
            name='adminuser',
            options={'verbose_name': '관리자', 'verbose_name_plural': '관리자 목록'},
        ),
        migrations.AlterField(
            model_name='adminuser',
            name='groups',
            field=models.ManyToManyField(blank=True, related_name='adminuser_groups', to='auth.group', verbose_name='그룹'),
        ),
        migrations.AlterField(
            model_name='adminuser',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='연락처'),
        ),
        migrations.AlterField(
            model_name='adminuser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, related_name='adminuser_permissions', to='auth.permission', verbose_name='사용자 권한'),
        ),
        migrations.CreateModel(
            name='DemandUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('company_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='회사명')),
                ('business_phone_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='대표번호')),
                ('contact_phone_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='담당자 연락처')),
                ('address', models.CharField(blank=True, max_length=255, null=True, verbose_name='주소')),
                ('address_detail', models.CharField(blank=True, max_length=255, null=True, verbose_name='상세 주소')),
                ('recommend_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='추천인 아이디')),
                ('is_approved', models.BooleanField(default=False, verbose_name='승인 여부')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일')),
                ('groups', models.ManyToManyField(blank=True, related_name='demanduser_groups', to='auth.group', verbose_name='그룹')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='demanduser_permissions', to='auth.permission', verbose_name='사용자 권한')),
            ],
            options={
                'verbose_name': '수요업체 사용자',
                'verbose_name_plural': '수요업체 사용자 목록',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ProviderUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('company_name', models.CharField(max_length=255, verbose_name='업체명')),
                ('business_registration_number', models.CharField(max_length=20, unique=True, verbose_name='사업자등록번호')),
                ('business_phone_number', models.CharField(max_length=20, verbose_name='대표번호')),
                ('consultation_phone_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='상담번호')),
                ('address', models.CharField(max_length=255, verbose_name='주소')),
                ('address_detail', models.CharField(blank=True, max_length=255, null=True, verbose_name='상세 주소')),
                ('is_approved', models.BooleanField(default=False, verbose_name='승인 여부')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일')),
                ('groups', models.ManyToManyField(blank=True, related_name='provideruser_groups', to='auth.group', verbose_name='그룹')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='provideruser_permissions', to='auth.permission', verbose_name='사용자 권한')),
            ],
            options={
                'verbose_name': '대행사 사용자',
                'verbose_name_plural': '대행사 사용자 목록',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
