# Generated by Django 4.1.7 on 2023-06-20 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0003_alter_teacher_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
