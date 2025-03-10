# Generated by Django 5.1.6 on 2025-03-05 03:08

import django.db.models.deletion
import estimates.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estimates', '0005_alter_estimate_service_category'),
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estimate',
            name='service_category',
            field=models.ForeignKey(blank=True, default=estimates.models.get_default_service_category, null=True, on_delete=django.db.models.deletion.CASCADE, to='services.servicecategory', verbose_name='서비스 카테고리'),
        ),
    ]
