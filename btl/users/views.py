from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count
from .models import UserProfile, Department
from .forms import UserForm, DepartmentForm
from django.contrib.auth.models import User

def is_admin(user):
    try:
        return user.userprofile.is_admin
    except:
        return False

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_departments = Department.objects.count()
    total_users = UserProfile.objects.count()
    documents_per_department = Department.objects.annotate(num_documents=Count('documents')).values('name', 'num_documents')
    users_per_department = Department.objects.annotate(num_users=Count('users')).values('name', 'num_users')
    return render(request, 'users/admin_dashboard.html', {
        'total_departments': total_departments,
        'total_users': total_users,
        'documents_per_department': documents_per_department,
        'users_per_department': users_per_department,
    })

@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = UserProfile.objects.all()
    return render(request, 'users/user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Get role from form
            role = form.cleaned_data.get('role', 'user')

            # Create UserProfile
            common_dept = Department.objects.get(is_common=True)
            admin_dept = Department.objects.get(name='Quản trị')

            user_profile = UserProfile.objects.create(
                user=user,
                position=form.cleaned_data.get('position', ''),
                is_admin=(role == 'admin')
            )

            # Add user to common department always
            user_profile.departments.add(common_dept)

            # If creating admin user, also add to admin department
            if role == 'admin':
                user_profile.departments.add(admin_dept)
            else:
                # For user role, add selected department
                selected_dept = form.cleaned_data.get('department')
                if selected_dept:
                    user_profile.departments.add(selected_dept)

            user_profile.save()

            role_text = "Admin" if role == 'admin' else "User"
            messages.success(request, f'{role_text} created successfully.')
            return redirect('users:user_list')
    else:
        form = UserForm()
    return render(request, 'users/user_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def user_update(request, pk):
    user_profile = get_object_or_404(UserProfile, pk=pk)

    # Only allow editing if:
    # 1. User is editing themselves, OR
    # 2. User is admin editing a regular user (not another admin)
    # Note: Admin cannot edit other admins, but can edit regular users
    if user_profile.is_admin and request.user != user_profile.user:
        messages.error(request, 'You cannot edit other admin users.')
        return redirect('users:user_list')

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user_profile.user)
        if form.is_valid():
            # Get role from form
            role = form.cleaned_data.get('role', 'user')

            # Check if user is trying to change their own role from admin to user
            # and they are the last admin
            if (request.user == user_profile.user and
                user_profile.is_admin and
                role == 'user'):

                # Count total admins
                total_admins = UserProfile.objects.filter(is_admin=True).count()

                if total_admins == 1:
                    messages.error(request, 'Cannot change role from Admin to User. At least one admin must remain in the system.')
                    return redirect('users:user_list')

            user = form.save()
            user_profile.is_admin = (role == 'admin')

            # Update departments: always include common department
            common_dept = Department.objects.get(is_common=True)
            admin_dept = Department.objects.get(name='Quản trị')

            user_profile.departments.clear()
            user_profile.departments.add(common_dept)

            # If user is admin, also add to admin department
            if role == 'admin':
                user_profile.departments.add(admin_dept)
            else:
                # For user role, add selected department
                selected_dept = form.cleaned_data.get('department')
                if selected_dept:
                    user_profile.departments.add(selected_dept)

            user_profile.position = form.cleaned_data.get('position', '')
            user_profile.save()

            role_text = "Admin" if role == 'admin' else "User"
            messages.success(request, f'{role_text} updated successfully.')
            return redirect('users:user_list')
    else:
        # For initial form, pick one department other than common if exists
        initial_dept = None
        for dept in user_profile.departments.all():
            if not dept.is_common:
                initial_dept = dept
                break

        # Set initial role based on current user status
        initial_role = 'admin' if user_profile.is_admin else 'user'

        # For admin users, don't set initial department since it won't be used
        if user_profile.is_admin:
            initial_dept = None

        form = UserForm(instance=user_profile.user, initial={
            'department': initial_dept,
            'position': user_profile.position,
            'role': initial_role
        })
    return render(request, 'users/user_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def user_delete(request, pk):
    user_profile = get_object_or_404(UserProfile, pk=pk)

    # Check if trying to delete self
    is_self_delete = (request.user == user_profile.user)

    # Check if user is admin
    is_admin_user = user_profile.is_admin

    # Count total admins
    total_admins = UserProfile.objects.filter(is_admin=True).count()

    # Permission checks - only allow deleting if:
    # 1. User is deleting themselves, OR
    # 2. User is admin deleting a regular user (not another admin)
    # Note: Admin cannot delete other admins, but can delete regular users
    if is_admin_user and not is_self_delete:
        # Cannot delete other admins
        messages.error(request, 'You cannot delete other admin users.')
        return redirect('users:user_list')

    if is_admin_user and is_self_delete and total_admins == 1:
        # Cannot delete the last admin
        messages.error(request, 'Cannot delete the last admin user. At least one admin must remain.')
        return redirect('users:user_list')

    if request.method == 'POST':
        try:
            # Delete user - this will cascade to UserProfile and related departments
            user_profile.user.delete()
            messages.success(request, 'User deleted successfully.')
            return redirect('users:user_list')
        except Exception as e:
            messages.error(request, f'Error deleting user: {str(e)}')
            return redirect('users:user_list')

    return render(request, 'users/user_confirm_delete.html', {
        'user_profile': user_profile,
        'is_self_delete': is_self_delete,
        'is_admin_user': is_admin_user
    })

@login_required
def user_profile_update(request):
    if request.method == 'POST':
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            # Get role from form
            role = form.cleaned_data.get('role', 'user')

            # Check if user is trying to change their own role from admin to user
            # and they are the last admin
            if (request.user.userprofile.is_admin and role == 'user'):
                # Count total admins
                total_admins = UserProfile.objects.filter(is_admin=True).count()

                if total_admins == 1:
                    messages.error(request, 'Cannot change role from Admin to User. At least one admin must remain in the system.')
                    return redirect('documents:document_list')

            user = form.save()
            request.user.userprofile.is_admin = (role == 'admin')
            request.user.userprofile.position = form.cleaned_data.get('position', '')
            request.user.userprofile.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('documents:document_list')
    else:
        form = UserForm(instance=request.user, initial={'position': request.user.userprofile.position})
    return render(request, 'users/user_profile_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'users/department_list.html', {'departments': departments})

@login_required
@user_passes_test(is_admin)
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department created successfully.')
            return redirect('users:department_list')
    else:
        form = DepartmentForm()
    return render(request, 'users/department_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def department_update(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if department.is_common:
        messages.error(request, 'Cannot edit the common department.')
        return redirect('users:department_list')
    if department.is_admin_department:
        messages.error(request, 'Cannot edit the admin department "Quản trị". This department is protected.')
        return redirect('users:department_list')
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully.')
            return redirect('users:department_list')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'users/department_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if department.is_common:
        messages.error(request, 'Cannot delete the common department.')
        return redirect('users:department_list')
    if department.is_admin_department:
        messages.error(request, 'Cannot delete the admin department "Quản trị". This department is protected and used for admin document sharing.')
        return redirect('users:department_list')
    if request.method == 'POST':
        # Remove the department from all users' departments (since they have common)
        for user_profile in UserProfile.objects.all():
            user_profile.departments.remove(department)
        department.delete()
        messages.success(request, 'Department deleted successfully.')
        return redirect('users:department_list')
    return render(request, 'users/user_confirm_delete.html', {'department': department})
