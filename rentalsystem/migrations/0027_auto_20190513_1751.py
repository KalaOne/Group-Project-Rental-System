# Generated by Django 2.1.7 on 2019-05-13 16:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rentalsystem', '0026_auto_20190513_1345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='address',
            field=models.ForeignKey(db_column='address_id', default=1, on_delete=django.db.models.deletion.PROTECT, to='rentalsystem.Address'),
        ),
    ]