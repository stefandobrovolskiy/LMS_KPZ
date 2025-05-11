from django.shortcuts import redirect, render
from courses.views import course_list_view

def home(request):
    return course_list_view(request)