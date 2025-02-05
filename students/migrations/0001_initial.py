# Generated by Django 4.1.7 on 2023-09-19 11:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('teachers', '0001_initial'),
        ('departments', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(blank=True, max_length=30, null=True)),
                ('last_name', models.CharField(blank=True, max_length=30, null=True)),
                ('full_name', models.CharField(blank=True, max_length=60, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('phone', models.CharField(blank=True, max_length=15, null=True, unique=True)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('address', models.CharField(blank=True, max_length=100, null=True)),
                ('roll', models.CharField(max_length=7, unique=True)),
                ('cgpa', models.FloatField(blank=True, null=True)),
                ('dept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='departments.department')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='departments.section')),
                ('series', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='departments.series')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='student', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StudentCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed', models.BooleanField(default=False)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='taken_by', to='departments.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='takes', to='students.student')),
            ],
        ),
        migrations.CreateModel(
            name='TheoryCourse',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('total_marks', models.IntegerField()),
                ('obtained_marks', models.IntegerField()),
                ('sectionA', models.IntegerField()),
                ('sectionB', models.IntegerField()),
                ('attendance', models.IntegerField()),
                ('examfor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_exams', to='students.studentcourse')),
                ('grade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='departments.gradepoint')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LabCourse',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('total_marks', models.IntegerField()),
                ('obtained_marks', models.IntegerField()),
                ('viva', models.IntegerField()),
                ('labPerformance', models.IntegerField()),
                ('labReport', models.IntegerField(blank=True, null=True)),
                ('attendance', models.IntegerField()),
                ('labquiz', models.IntegerField(blank=True, null=True)),
                ('labfinal', models.IntegerField(blank=True, null=True)),
                ('examfor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_exams', to='students.studentcourse')),
                ('grade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='departments.gradepoint')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ClassTest',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('full_marks', models.IntegerField()),
                ('obtained_marks', models.IntegerField(default=0)),
                ('ct_for', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='class_tests', to='students.studentcourse')),
                ('taken_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='class_tests', to='teachers.teacher')),
            ],
        ),
    ]
