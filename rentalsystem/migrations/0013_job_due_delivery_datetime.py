# Generated by Django 2.1.7 on 2019-03-27 10:25

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('rentalsystem', '0012_auto_20190327_1008'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='due_delivery_datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
