# Generated by Django 5.1.5 on 2025-04-11 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_banking', '0004_alter_transaction_rrn_alter_transaction_stan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='rrn',
            field=models.CharField(default='0000', max_length=20),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='stan',
            field=models.CharField(default='0000', max_length=12),
        ),
    ]
