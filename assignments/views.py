from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# from .models import Assignment  # Додайте свою модель Assignment
from .models import Assignment, StudentAssignmentSubmission
from courses.models import Lesson

# Create your views here.

@login_required
def assignment_detail(request, assignment_id):
    # assignment = get_object_or_404(Assignment, id=assignment_id)
    # return render(request, 'assignments/assignment_detail.html', {'assignment': assignment})
    pass  # Заглушка

@login_required
def assignment_edit(request, assignment_id):
    # assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.user.role == 'teacher' or request.user.role == 'admin':
        # return render(request, 'assignments/assignment_edit.html', {'assignment': assignment})
        pass  # Заглушка
    else:
        return redirect('core:home')

@login_required
def assignment_create(request):
    if request.user.role == 'teacher' or request.user.role == 'admin':
        # return render(request, 'assignments/assignment_create.html')
        pass  # Заглушка
    else:
        return redirect('core:home')

@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    lesson = assignment.lesson
    if request.method == 'POST':
        submission_url = request.POST.get('submission_url')
        upload_file = request.FILES.get('upload_file')
        if submission_url or upload_file:
            StudentAssignmentSubmission.objects.update_or_create(
                student=request.user,
                assignment=assignment,
                lesson=lesson,
                defaults={'submission_url': submission_url, 'upload_file': upload_file}
            )
            messages.success(request, 'Роботу успішно здано!')
        else:
            messages.error(request, 'Потрібно додати посилання або файл!')
        return redirect('courses:course_detail', slug=lesson.module.course.slug)
    return redirect('courses:course_detail', slug=lesson.module.course.slug)

@login_required
def submit_assignment_by_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    assignment = Assignment.objects.filter(lesson=lesson).first()
    if not assignment:
        messages.error(request, "Для цього уроку не створено завдання. Зверніться до викладача.")
        return redirect('courses:course_detail', slug=lesson.module.course.slug)
    if request.method == 'POST':
        submission_url = request.POST.get('submission_url')
        upload_file = request.FILES.get('upload_file')
        if submission_url or upload_file:
            StudentAssignmentSubmission.objects.update_or_create(
                student=request.user,
                assignment=assignment,
                lesson=lesson,
                defaults={'submission_url': submission_url, 'upload_file': upload_file}
            )
            messages.success(request, f"Роботу для '{lesson.title}' успішно здано!")
        else:
            messages.error(request, f"Будь ласка, надайте посилання на роботу або завантажте файл.")
        return redirect('courses:course_detail', slug=lesson.module.course.slug)
    return redirect('courses:course_detail', slug=lesson.module.course.slug)
