# Generated by Django 2.1.7 on 2019-05-13 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentalsystem', '0022_auto_20190512_1142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='info',
            field=models.CharField(blank=True, max_length=5000),
        ),
    ]
