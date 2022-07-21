# Generated by Django 3.2.6 on 2021-10-20 09:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('customAdmin', '0004_auto_20211020_0906'),
        ('customUser', '0002_alter_orderproductdetails_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='couponusage',
            name='used_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='orderproductdetails',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='customAdmin.product'),
        ),
        migrations.AlterField(
            model_name='orders',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='productreview',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='customAdmin.product'),
        ),
    ]
