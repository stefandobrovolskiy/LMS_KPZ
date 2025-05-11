from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    path('submit/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
    path('submit/lesson/<int:lesson_id>/', views.submit_assignment_by_lesson, name='submit_assignment_by_lesson'),
] 