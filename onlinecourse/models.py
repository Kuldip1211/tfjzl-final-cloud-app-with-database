import sys
from django.conf import settings
from django.db import models
from django.utils.timezone import now

try:
    from django.db import models
except Exception:
    print("Django is not installed.")
    sys.exit()


class Instructor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField()

    class Meta:
        ordering = ["user__username"]

    def __str__(self):
        return f"{self.user.username}"


class Learner(models.Model):

    class Occupation(models.TextChoices):
        STUDENT = "student", "Student"
        DEVELOPER = "developer", "Developer"
        DATA_SCIENTIST = "data_scientist", "Data Scientist"
        DATABASE_ADMIN = "dba", "Database Admin"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    occupation = models.CharField(
        max_length=20,
        choices=Occupation.choices,
        default=Occupation.STUDENT
    )

    social_link = models.URLField(max_length=200)

    class Meta:
        ordering = ["user__username"]

    def __str__(self):
        return f"{self.user.username}, {self.get_occupation_display()}"


class Course(models.Model):
    name = models.CharField(
        max_length=30,
        default="online course"
    )

    image = models.ImageField(upload_to="course_images/")

    description = models.CharField(max_length=1000)

    pub_date = models.DateField(null=True)

    instructors = models.ManyToManyField(Instructor)

    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Enrollment"
    )

    total_enrollment = models.IntegerField(default=0)

    is_enrolled = False

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.description}"


class Lesson(models.Model):
    title = models.CharField(max_length=200, default="title")
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        ordering = ["order"]


class Enrollment(models.Model):

    class CourseMode(models.TextChoices):
        AUDIT = "audit", "Audit"
        HONOR = "honor", "Honor"
        BETA = "BETA", "BETA"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    date_enrolled = models.DateField(default=now)

    mode = models.CharField(
        max_length=5,
        choices=CourseMode.choices,
        default=CourseMode.AUDIT
    )

    rating = models.FloatField(default=5.0)


class Question(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    content = models.CharField(max_length=200)

    grade = models.IntegerField(default=50)

    def __str__(self):
        return f"Question: {self.content}"

    def is_get_score(self, selected_ids):
        correct_choice_ids = set(
            self.choice_set.filter(is_correct=True)
            .values_list("id", flat=True)
        )

        submitted_choice_ids = set(selected_ids)

        return correct_choice_ids.issubset(submitted_choice_ids)


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    content = models.CharField(max_length=200)

    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.content


class Submission(models.Model):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE
    )

    choices = models.ManyToManyField(Choice)