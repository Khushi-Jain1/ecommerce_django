# Generated by Django 3.2.6 on 2021-10-22 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customAdmin', '0010_auto_20211021_1927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='shipping_required',
            field=models.BooleanField(default=True),
        ),
    ]
