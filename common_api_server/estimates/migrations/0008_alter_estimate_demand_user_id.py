# Generated by Django 5.1.6 on 2025-03-05 03:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estimates', '0007_estimate_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estimate',
            name='demand_user_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='수요업체 사용자 ID'),
        ),
    ]
