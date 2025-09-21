from django.db import migrations


def update_admin_department_assignment(apps, schema_editor):
    """Ensure all admin users are in both common and admin departments"""
    Department = apps.get_model('users', 'Department')
    UserProfile = apps.get_model('users', 'UserProfile')

    try:
        # Get common and admin departments
        common_dept = Department.objects.get(is_common=True)
        admin_dept = Department.objects.get(name='Quản trị')

        # Get all admin users
        admin_profiles = UserProfile.objects.filter(is_admin=True)

        # Ensure each admin is in both departments
        for profile in admin_profiles:
            if common_dept not in profile.departments.all():
                profile.departments.add(common_dept)
            if admin_dept not in profile.departments.all():
                profile.departments.add(admin_dept)
            profile.save()

    except Department.DoesNotExist:
        # If departments don't exist, skip this migration
        pass


def reverse_func(apps, schema_editor):
    """Remove admin department from admin users (reverse operation)"""
    Department = apps.get_model('users', 'Department')
    UserProfile = apps.get_model('users', 'UserProfile')

    try:
        admin_dept = Department.objects.get(name='Quản trị')
        admin_profiles = UserProfile.objects.filter(is_admin=True)

        for profile in admin_profiles:
            profile.departments.remove(admin_dept)
            profile.save()
    except Department.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_set_created_by_for_existing_departments'),
    ]

    operations = [
        migrations.RunPython(update_admin_department_assignment, reverse_func),
    ]
