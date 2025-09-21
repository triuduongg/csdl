from django.urls import path, include
from . import views

app_name = 'users'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),  # login, logout, password management
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.user_list, name='user_list'),
    path('admin/users/create/', views.user_create, name='user_create'),
    path('admin/users/<int:pk>/update/', views.user_update, name='user_update'),
    path('admin/users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('admin/departments/', views.department_list, name='department_list'),
    path('admin/departments/create/', views.department_create, name='department_create'),
    path('admin/departments/<int:pk>/update/', views.department_update, name='department_update'),
    path('admin/departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
]
