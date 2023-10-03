# Generated by Django 4.1.7 on 2023-09-30 16:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Main', '0002_transaction_valid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='paid_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='transactions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='paid_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='received_transactions', to=settings.AUTH_USER_MODEL),
        ),
    ]
