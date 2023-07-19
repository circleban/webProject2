# Generated by Django 4.1.7 on 2023-06-28 10:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=10, unique=True)),
                ('name', models.CharField(max_length=64)),
                ('type', models.CharField(choices=[('Theory', 'Theory'), ('Lab', 'Lab')], default='Theory', max_length=10)),
                ('isAllocated', models.BooleanField(default=False)),
                ('credit', models.DecimalField(decimal_places=2, default=0.0, max_digits=3)),
                ('description', models.JSONField(blank=True, null=True)),
            ],
            options={
                'ordering': ['semester', 'title'],
            },
        ),
        migrations.CreateModel(
            name='courseRegistration',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('finished', 'Finished')], default='pending', max_length=10)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('fee', models.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dept_id', models.CharField(max_length=4, unique=True)),
                ('dept_code', models.CharField(blank=True, max_length=5, null=True, unique=True)),
                ('dept_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Semester',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('sem_no', models.IntegerField()),
                ('year', models.CharField(max_length=4)),
                ('year_sem', models.CharField(max_length=4)),
                ('dept', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='semesters', to='departments.department')),
            ],
        ),
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=10, unique=True)),
                ('admit_year', models.IntegerField(unique=True)),
                ('is_running', models.BooleanField(default=True)),
                ('end_year', models.IntegerField(blank=True, null=True)),
                ('maximum_students', models.IntegerField(blank=True, null=True)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='series', to='departments.department')),
                ('running_semester', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='running_series', to='departments.semester')),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=10, unique=True)),
                ('series', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='departments.series')),
            ],
        ),
    ]
