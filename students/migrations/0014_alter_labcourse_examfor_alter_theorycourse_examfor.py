# Generated by Django 4.1.7 on 2023-10-02 18:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0013_alter_classtest_obtained_marks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='labcourse',
            name='examfor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_exams', to='students.studentcourse'),
        ),
        migrations.AlterField(
            model_name='theorycourse',
            name='examfor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_exams', to='students.studentcourse'),
        ),
    ]
