# Generated by Django 2.1.7 on 2019-05-13 13:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rentalsystem', '0024_auto_20190513_1340'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='county',
        ),
    ]
