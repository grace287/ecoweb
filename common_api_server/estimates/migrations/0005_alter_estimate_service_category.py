# Generated by Django 5.1.6 on 2025-03-01 00:59

import django.db.models.deletion
import estimates.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estimates', '0004_alter_estimate_service_category'),
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estimate',
            name='service_category',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='services.servicecategory', verbose_name='서비스 카테고리'),
        ),
    ]
