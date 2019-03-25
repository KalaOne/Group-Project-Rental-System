# Generated by Django 2.1.7 on 2019-03-25 12:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rentalsystem', '0004_auto_20190325_1139'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemCategoryPair',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rentalsystem.Category')),
                ('item_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rentalsystem.Item')),
            ],
        ),
    ]
