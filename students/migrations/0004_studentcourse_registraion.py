# Generated by Django 4.1.7 on 2023-10-01 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0003_alter_student_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentcourse',
            name='registraion',
            field=models.CharField(choices=[('R', 'Registered'), ('N', 'Not Registered')], default='R', max_length=10),
        ),
    ]
