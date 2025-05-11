from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list_view, name='course_list'),
    path('<slug:slug>/', views.course_detail_view, name='course_detail'),
    path('create/', views.course_create, name='course_create'),
    path('<slug:slug>/update/', views.course_update, name='course_update'),
    path('<slug:slug>/edit/', views.course_edit, name='course_edit'),
    path('<slug:slug>/delete/', views.course_delete, name='course_delete'),
    path('<slug:course_slug>/module/create/', views.module_create, name='module_create'),
    path('module/<int:module_id>/update/', views.module_update, name='module_update'),
    path('module/<int:module_id>/delete/', views.module_delete, name='module_delete'),
    path('module/<int:module_id>/lesson/create/', views.lesson_create, name='lesson_create'),
    path('lesson/<int:lesson_id>/update/', views.lesson_update, name='lesson_update'),
    path('lesson/<int:lesson_id>/delete/', views.lesson_delete, name='lesson_delete'),
    path('<slug:course_slug>/download_certificate/', views.download_certificate, name='download_certificate'),
] 