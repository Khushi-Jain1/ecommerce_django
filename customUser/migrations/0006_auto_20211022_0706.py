# Generated by Django 3.2.6 on 2021-10-22 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customUser', '0005_alter_paymentdetails_transaction_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentdetails',
            name='email',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='paymentdetails',
            name='name',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='paymentdetails',
            name='payment_mode',
            field=models.CharField(default='netbanking', max_length=50),
        ),
        migrations.AlterField(
            model_name='paymentdetails',
            name='payment_status',
            field=models.CharField(max_length=50, null=True),
        ),
    ]