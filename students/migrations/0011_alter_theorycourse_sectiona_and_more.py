# Generated by Django 4.1.7 on 2023-10-02 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0010_alter_classtest_taken_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='theorycourse',
            name='sectionA',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='theorycourse',
            name='sectionB',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
