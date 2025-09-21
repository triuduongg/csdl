from django import forms
from .models import Document
from users.models import Department


class DocumentForm(forms.ModelForm):
    target_departments = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all(),
        widget=forms.SelectMultiple,
        required=False,
        label="Phòng ban"
    )

    class Meta:
        model = Document
        fields = ['title', 'description', 'file', 'visibility_type', 'target_departments']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Always set visibility to department
        self.fields['visibility_type'].widget = forms.HiddenInput()
        self.fields['visibility_type'].initial = 'department'
        self.fields['visibility_type'].required = False

        # For editing, file is not required (user can keep existing file)
        if self.instance and self.instance.pk:
            self.fields['file'].required = False
            self.fields['file'].label = 'Chọn file mới (không bắt buộc)'
        else:
            # For creating new document, file is required
            self.fields['file'].required = True
            self.fields['file'].label = 'Chọn file'

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (limit to 50MB)
            if file.size > 50 * 1024 * 1024:
                raise forms.ValidationError('File size must be less than 50MB.')

            # Check file extension
            allowed_extensions = [
                '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                '.txt', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.rar'
            ]

            file_name = file.name.lower()
            if not any(file_name.endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError(
                    f'File type not supported. Allowed types: {", ".join(allowed_extensions)}'
                )

        return file
