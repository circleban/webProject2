# Generated by Django 4.1.7 on 2023-09-19 11:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('departments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('first_name', models.CharField(blank=True, max_length=30, null=True)),
                ('last_name', models.CharField(blank=True, max_length=30, null=True)),
                ('full_name', models.CharField(blank=True, max_length=60, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('phone', models.CharField(blank=True, max_length=15, null=True, unique=True)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('address', models.CharField(blank=True, max_length=100, null=True)),
                ('code', models.CharField(max_length=5)),
                ('joined', models.DateField(auto_now_add=True)),
                ('intro', models.TextField(blank=True, null=True)),
                ('designation', models.CharField(choices=[('Professor', 'Professor'), ('Assistant Professor', 'Assistant Professor'), ('Associate Professor', 'Associate Professor'), ('Lecturer', 'Lecturer')], default='Lecturer', max_length=20)),
                ('status', models.CharField(choices=[('Active', 'Active'), ('On Leave', 'On Leave'), ('Retired', 'Retired')], default='Active', max_length=10)),
                ('dept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teachers', to='departments.department')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='teacher', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='courseTeacherAssignment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('Active', 'Active'), ('Finished', 'Finished')], default='Active', max_length=10)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teachers', to='departments.course')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='allocations', to='departments.section')),
                ('series', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='allocations', to='departments.series')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='teachers.teacher')),
            ],
        ),
        migrations.AddConstraint(
            model_name='teacher',
            constraint=models.UniqueConstraint(fields=('code', 'dept'), name='unique_teacher'),
        ),
        migrations.AddConstraint(
            model_name='courseteacherassignment',
            constraint=models.UniqueConstraint(fields=('course', 'teacher', 'series', 'section'), name='unique_course_teacher'),
        ),
    ]
