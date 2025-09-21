from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_common = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_departments', blank=True, null=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='updated_departments', blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def is_admin_department(self):
        """Check if this is the admin department"""
        return self.name == 'Quản trị'

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    departments = models.ManyToManyField(Department, related_name='users', blank=True)
    position = models.CharField(max_length=100, blank=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
