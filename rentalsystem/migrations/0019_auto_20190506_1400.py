# Generated by Django 2.1.7 on 2019-05-06 13:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rentalsystem', '0018_auto_20190417_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='job_list_id',
            field=models.ForeignKey(blank=True, db_column='job_list_id', on_delete=django.db.models.deletion.PROTECT, to='rentalsystem.JobList'),
        ),
    ]
