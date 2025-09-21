from django.db import migrations, models
from django.contrib.auth.hashers import make_password

def create_admin_and_common_department(apps, schema_editor):
    Department = apps.get_model('users', 'Department')
    UserProfile = apps.get_model('users', 'UserProfile')
    User = apps.get_model('auth', 'User')

    # Create common department if not exists
    common_dept, created = Department.objects.get_or_create(name='Common', defaults={'is_common': True})

    # Create admin user if not exists
    admin_user, created = User.objects.get_or_create(username='admin', defaults={
        'is_staff': True,
        'is_superuser': True,
        'password': make_password('adminpassword')
    })

    # Create UserProfile for admin
    admin_profile, created = UserProfile.objects.get_or_create(user=admin_user)
    admin_profile.department = common_dept
    admin_profile.is_admin = True
    admin_profile.save()

def reverse_func(apps, schema_editor):
    # Optional: delete admin user and common department on migration rollback
    Department = apps.get_model('users', 'Department')
    User = apps.get_model('auth', 'User')

    User.objects.filter(username='admin').delete()
    Department.objects.filter(name='Common').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_department_userprofile_is_admin_and_more'),
    ]

    operations = [
        migrations.RunPython(create_admin_and_common_department, reverse_func),
    ]
