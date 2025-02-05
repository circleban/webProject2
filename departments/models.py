from collections.abc import Iterable
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.


class Department(models.Model):
    dept_id = models.CharField(max_length=4, unique=True)
    dept_code = models.CharField(max_length=5, unique=True, null=True, blank=True)
    dept_name = models.CharField(max_length=50)
    head = models.OneToOneField(
        "teachers.Teacher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dept_head",
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="dept"
    )

    def __str__(self) -> str:
        return f"{self.dept_id}: {self.dept_name}"

    def get_absolute_url(self):
        return reverse("dept:home", kwargs={"deptId": self.dept_id})


class Semester(models.Model):
    id = models.AutoField(primary_key=True)
    sem_no = models.IntegerField()
    year = models.CharField(max_length=4)
    year_sem = models.CharField(max_length=4)
    dept = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="semesters"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["sem_no", "dept"], name="unique_semester")
        ]

    def __str__(self) -> str:
        return f"{self.year} year {self.year_sem} semester"

    def save(self, *args, **kwargs):
        import math

        serial_map = {1: "st", 2: "nd", 3: "rd", 4: "th"}
        yr = math.ceil(self.sem_no / 2)
        sem = "Odd" if self.sem_no % 2 else "Even"
        self.year = f"{yr}{serial_map[yr]}"
        self.year_sem = f"{sem}"
        super().save(*args, **kwargs)


class Course(models.Model):
    id = models.AutoField(primary_key=True)
    th = "Theory"
    lab = "Lab"
    type_choices = [(th, "Theory"), (lab, "Lab")]

    title = models.CharField(max_length=10, unique=True)  # ex - CSE1100
    name = models.CharField(max_length=64)
    type = models.CharField(max_length=10, choices=type_choices, default=th)
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, related_name="courses"
    )
    isAllocated = models.BooleanField(default=False)
    credit = models.DecimalField(max_digits=3, decimal_places=2)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="courses"
    )
    description = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ["semester", "title"]

    def __str__(self) -> str:
        return f"{self.title}: {self.name}, Semester: {self.semester}"

    def isTheoryCourse(self):
        return self.type == self.th

    def edit_course_url(self):
        return reverse(
            "dept:editCourse",
            kwargs={"deptId": self.department.dept_id, "courseId": self.title},
        )

    def delete_course_url(self):
        return reverse(
            "dept:deleteCourse",
            kwargs={"deptId": self.department.dept_id, "courseId": self.title},
        )


class courseRegistration(models.Model):
    id = models.AutoField(primary_key=True)
    status_choices = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("finished", "Finished"),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default="pending")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    series = models.OneToOneField(
        "Series", on_delete=models.CASCADE, related_name="courseReg"
    )
    fee = models.JSONField(null=True, blank=True)

    def __str__(self) -> str:
        self.check_deadline()
        return f"{self.series.name} course registration: {self.status}"

    def isRunning(self) -> bool:
        self.check_deadline()
        return self.status == "running"

    def check_deadline(self):
        from datetime import date

        today = date.today()
        if self.status == "running" and today > self.end_date:
            self.status = "finished"
            self.save()


class Series(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10, unique=True)  # Ex - CSE99
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="series"
    )
    admit_year = models.IntegerField(unique=True)
    running_semester = models.OneToOneField(
        Semester, on_delete=models.CASCADE, related_name="running_series"
    )
    is_running = models.BooleanField(default=True)
    end_year = models.IntegerField(null=True, blank=True)
    maximum_students = models.IntegerField(null=True, blank=True)
    exam_status = models.CharField(max_length=10, choices=[
        ("NR", "Not Running"),
        ("R", "Running"),
        ("F", "Finished")
    ], default="NR")

    def __str__(self) -> str:
        return (
            f"{self.name}, {self.admit_year}, Running semester: {self.running_semester}"
        )
    def complete_semester(self):
        self.exam_status = "NR"
        self.courseReg.status = "pending"
        self.update_semester()
        self.courseReg.save()
        self.save()
    def update_semester(self):
        if self.running_semester.sem_no == self.department.semesters.count():
            self.is_running = False
        else:
            self.running_semester = self.department.semesters.get(sem_no=self.running_semester.sem_no + 1)
    def get_absolute_url_control_panel(self):
        return reverse(
            "dept:seriesControlPanel",
            kwargs={"deptId": self.department.dept_id, "serId": self.id},
        )

    def get_absolute_url_course_allocation(self):
        return reverse(
            "dept:courseTeacherAllocation",
            kwargs={"deptId": self.department.dept_id, "serId": self.id},
        )
    def get_absolute_url_result(self):
        return reverse(
            "dept:result",
            kwargs={"deptId": self.department.dept_id, "serId": self.id},
        )


class Section(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=10, unique=True)  # Ex - CSE99A
    series = models.ForeignKey(
        Series, on_delete=models.CASCADE, related_name="sections"
    )
    maximum_students = models.IntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.name}, {self.series.name}"


class GradePoint(models.Model):
    id = models.AutoField(primary_key=True)
    grade = models.CharField(max_length=2, unique=True)
    point = models.DecimalField(max_digits=3, decimal_places=2)
    minimum_marks = models.IntegerField()
    maximum_marks = models.IntegerField(null=True, blank=True)
    def __str__(self) -> str:
        return f"{self.grade}: {self.point}"
