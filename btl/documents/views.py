from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q
from .models import Document
from .forms import DocumentForm
from users.models import UserProfile
import os
import mimetypes


@login_required
def document_list(request):
    user_profile = UserProfile.objects.get(user=request.user)
    user_departments = user_profile.departments.all()

    # Documents visible to the user: documents sent to any of user's departments
    # Order by upload_date descending (newest first)
    documents = Document.objects.filter(target_departments__in=user_departments).distinct().order_by('-upload_date')

    return render(request, 'documents/document_list.html', {'documents': documents})


@login_required
def upload_document(request):
    if request.method == 'POST':
        # Debug: Print form data and files
        print("POST data:", request.POST)
        print("FILES data:", request.FILES)

        form = DocumentForm(request.POST, request.FILES, user=request.user)

        # Debug: Check if file is detected
        if 'file' in request.FILES:
            print("File detected:", request.FILES['file'].name)
            print("File size:", request.FILES['file'].size)
        else:
            print("No file detected in request.FILES")

        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()
            form.save_m2m()
            return redirect('documents:document_list')
        else:
            # Debug: Print form errors
            print("Form errors:", form.errors)
            print("Non-field errors:", form.non_field_errors())
    else:
        form = DocumentForm(user=request.user)
    return render(request, 'documents/upload.html', {'form': form})


@login_required
def edit_document(request, pk):
    document = get_object_or_404(Document, pk=pk)

    # Check if current user is admin or the one who uploaded the document
    user_profile = UserProfile.objects.get(user=request.user)
    if not user_profile.is_admin and document.uploaded_by != request.user:
        return redirect('documents:document_list')

    if request.method == 'POST':
        # For editing, we need to handle the case where no new file is uploaded
        form = DocumentForm(request.POST, request.FILES, instance=document, user=request.user)

        # If no new file is uploaded, remove it from cleaned_data to avoid validation issues
        if not request.FILES.get('file'):
            form.data = form.data.copy()
            form.data['file'] = ''  # Clear the file field

        if form.is_valid():
            document = form.save(commit=False)
            document.save()
            form.save_m2m()
            return redirect('documents:document_list')
    else:
        form = DocumentForm(instance=document, user=request.user)

    return render(request, 'documents/edit_document.html', {'form': form, 'document': document})


@login_required
def delete_document(request, pk):
    document = get_object_or_404(Document, pk=pk)

    # Check if current user is admin or the one who uploaded the document
    user_profile = UserProfile.objects.get(user=request.user)
    if not user_profile.is_admin and document.uploaded_by != request.user:
        return redirect('documents:document_list')

    if request.method == 'POST':
        document.delete()
        return redirect('documents:document_list')

    return render(request, 'documents/delete_document.html', {'document': document})


def get_file_content_type(filename):
    """Get the correct content type for a file based on its extension"""
    content_type, _ = mimetypes.guess_type(filename)

    # Fallback mappings for common file types
    if content_type is None:
        ext = os.path.splitext(filename)[1].lower()
        content_type_map = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.txt': 'text/plain',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.zip': 'application/zip',
            '.rar': 'application/x-rar-compressed',
        }
        content_type = content_type_map.get(ext, 'application/octet-stream')

    return content_type


@login_required
def download_document(request, pk):
    document = get_object_or_404(Document, pk=pk)

    # Get the original filename
    original_filename = document.file.name
    if '/' in original_filename:
        original_filename = original_filename.split('/')[-1]

    # Determine content type based on file extension
    content_type = get_file_content_type(original_filename)

    # Create response with correct content type and filename
    response = HttpResponse(document.file, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{original_filename}"'

    return response


@login_required
def search_documents(request):
    query = request.GET.get('q', '').strip()

    # Get user's departments for permission filtering
    user_profile = UserProfile.objects.get(user=request.user)
    user_departments = user_profile.departments.all()

    # Base queryset: only documents visible to the user
    # Order by upload_date descending (newest first)
    documents = Document.objects.filter(target_departments__in=user_departments).distinct().order_by('-upload_date')

    # Apply search filter if query is provided
    if query:
        documents = documents.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    return render(request, 'documents/search.html', {'documents': documents, 'query': query})
