# Generated by Django 4.1.7 on 2023-09-30 17:35

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0003_alter_transaction_paid_by_alter_transaction_paid_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='time',
            field=models.TimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
