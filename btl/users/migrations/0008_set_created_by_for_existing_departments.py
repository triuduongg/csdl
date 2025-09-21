from django.db import migrations

def set_created_by_for_existing_departments(apps, schema_editor):
    Department = apps.get_model('users', 'Department')
    User = apps.get_model('auth', 'User')
    admin_user = User.objects.filter(is_superuser=True).first()
    if admin_user:
        for dept in Department.objects.filter(created_by__isnull=True):
            dept.created_by = admin_user
            dept.save()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_department_created_by_department_updated_by'),
    ]

    operations = [
        migrations.RunPython(set_created_by_for_existing_departments),
    ]
