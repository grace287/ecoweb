# Generated by Django 5.1.6 on 2025-03-07 02:33

import estimates.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estimates', '0008_alter_estimate_demand_user_id'),
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='estimate',
            name='service_category',
        ),
        migrations.AddField(
            model_name='estimate',
            name='service_categories',
            field=models.ManyToManyField(blank=True, default=estimates.models.get_default_service_category, null=True, related_name='estimates', to='services.servicecategory', verbose_name='서비스 카테고리'),
        ),
        migrations.AlterField(
            model_name='estimate',
            name='demand_user_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
