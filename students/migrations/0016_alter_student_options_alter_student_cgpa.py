# Generated by Django 4.1.7 on 2023-10-16 18:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0015_result'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='student',
            options={'ordering': ['roll']},
        ),
        migrations.AlterField(
            model_name='student',
            name='cgpa',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True),
        ),
    ]
