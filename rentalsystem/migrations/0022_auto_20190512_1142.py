# Generated by Django 2.1.7 on 2019-05-12 11:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rentalsystem', '0021_auto_20190508_0932'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='item_id',
            field=models.ForeignKey(db_column='item_id', on_delete=django.db.models.deletion.PROTECT, to='rentalsystem.ItemListing'),
        ),
    ]
