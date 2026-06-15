from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        EMPLOYER = 'employer', 'Employer'
        CANDIDATE = 'candidate', 'Candidate'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.username} ({self.role})"