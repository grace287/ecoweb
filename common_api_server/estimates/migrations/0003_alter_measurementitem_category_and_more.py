# Generated by Django 5.1.6 on 2025-03-01 00:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estimates', '0002_initial'),
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='measurementitem',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='services.servicecategory', verbose_name='측정 종류'),
        ),
        migrations.RemoveField(
            model_name='estimate',
            name='service_category',
        ),
        migrations.AlterModelOptions(
            name='estimateattachment',
            options={'verbose_name': '견적 첨부파일', 'verbose_name_plural': '견적 첨부파일 목록'},
        ),
        migrations.DeleteModel(
            name='ServiceCategory',
        ),
        migrations.AddField(
            model_name='estimate',
            name='service_category',
            field=models.ForeignKey(default='default-category-code', on_delete=django.db.models.deletion.CASCADE, to='services.servicecategory', verbose_name='서비스 카테고리'),
            preserve_default=False,
        ),
    ]
