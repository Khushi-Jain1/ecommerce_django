# Generated by Django 3.2.6 on 2021-10-21 18:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customUser', '0003_auto_20211020_0906'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderproductdetails',
            name='product',
        ),
    ]
