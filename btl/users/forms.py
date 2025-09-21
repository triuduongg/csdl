from django import forms
from django.contrib.auth.models import User
from .models import Department

class UserForm(forms.ModelForm):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True, label="Phòng ban")
    position = forms.CharField(max_length=100, required=False, label="Chức vụ")
    password1 = forms.CharField(label='Mật khẩu', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Xác nhận mật khẩu', widget=forms.PasswordInput)
    role = forms.ChoiceField(
        choices=[('user', 'User'), ('admin', 'Admin')],
        initial='user',
        label="Chức vụ hệ thống",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'department', 'position']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Editing existing user, make password optional
            self.fields['password1'].required = False
            self.fields['password2'].required = False
        else:
            # Creating new user, require password
            self.fields['password1'].required = True
            self.fields['password2'].required = True

        # Set department queryset based on role
        role = self.data.get('role') if self.data else None
        if not self.instance.pk:  # Creating new user
            if role == 'user':
                # User nhân viên có thể chọn tất cả departments trừ Quản trị
                try:
                    admin_dept = Department.objects.get(name='Quản trị')
                    self.fields['department'].queryset = Department.objects.exclude(id=admin_dept.id)
                    self.fields['department'].help_text = "Chọn phòng ban cho người dùng nhân viên (sẽ tự động thêm vào phòng ban chung)"
                except Department.DoesNotExist:
                    self.fields['department'].queryset = Department.objects.all()
            else:
                # Admin không cần chọn department vì sẽ tự động thêm vào Common + Quản trị
                self.fields['department'].widget = forms.HiddenInput()
                self.fields['department'].required = False
                self.fields['department'].help_text = "Admin sẽ tự động thuộc phòng ban chung và phòng ban quản trị"
        else:
            # Editing existing user
            if role == 'user':
                # User nhân viên có thể chọn tất cả departments trừ Quản trị
                try:
                    admin_dept = Department.objects.get(name='Quản trị')
                    self.fields['department'].queryset = Department.objects.exclude(id=admin_dept.id)
                    self.fields['department'].help_text = "Chọn phòng ban cho người dùng nhân viên (sẽ tự động thêm vào phòng ban chung)"
                except Department.DoesNotExist:
                    self.fields['department'].queryset = Department.objects.all()
            else:
                # Admin không cần chọn department
                self.fields['department'].widget = forms.HiddenInput()
                self.fields['department'].required = False
                self.fields['department'].help_text = "Admin sẽ tự động thuộc phòng ban chung và phòng ban quản trị"

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if self.instance and self.instance.pk:
            # Editing, only check if provided
            if password1 or password2:
                if password1 != password2:
                    raise forms.ValidationError("Mật khẩu không khớp.")
        else:
            # Creating, must have password
            if not password1 or not password2:
                raise forms.ValidationError("Mật khẩu là bắt buộc.")
            if password1 != password2:
                raise forms.ValidationError("Mật khẩu không khớp.")

        # Validate department assignment for user role
        role = cleaned_data.get('role')
        department = cleaned_data.get('department')

        if role == 'user' and department:
            try:
                admin_dept = Department.objects.get(name='Quản trị')
                if department.id == admin_dept.id:
                    raise forms.ValidationError("Người dùng nhân viên không được phép thuộc phòng ban Quản trị.")
            except Department.DoesNotExist:
                pass

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']
