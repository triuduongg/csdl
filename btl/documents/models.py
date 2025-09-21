from django.db import models
from django.contrib.auth.models import User
from users.models import Department


VISIBILITY_CHOICES = [
    ('department', 'Phòng ban'),
    ('specific', 'Người dùng cụ thể'),
]


class Document(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='documents/')
    target_departments = models.ManyToManyField(Department, related_name='documents', blank=True)
    target_users = models.ManyToManyField(User, related_name='target_documents', blank=True)
    visibility_type = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='department', blank=True)

    def __str__(self):
        return self.title
