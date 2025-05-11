from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Module, Lesson, StudentSubmission, Announcement, Event
from .forms import CourseForm, ModuleForm, LessonForm
from assignments.models import StudentAssignmentSubmission
from django.http import HttpResponse
from .utils import generate_certificate_html
import datetime

# Create your views here.

def course_list(request):
    courses = Course.objects.filter(is_published=True)
    return render(request, 'courses/course_list.html', {'courses': courses})

@login_required
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    modules = course.modules.all().order_by('order').prefetch_related('lessons')
    submitted_assignments = []
    submissions_by_lesson = {}
    if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'student':
        submissions = StudentAssignmentSubmission.objects.filter(
            student=request.user,
            lesson__module__course=course
        ).select_related('lesson')
        submitted_assignments = [sub.lesson.id for sub in submissions]
        submissions_by_lesson = {sub.lesson.id: sub for sub in submissions}
    list(messages.get_messages(request))  # Очищення повідомлень
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'modules': modules,
        'submitted_assignments': submitted_assignments,
        'submissions_by_lesson': submissions_by_lesson
    })

@login_required
def course_create(request):
    if request.user.role != 'admin':
        return redirect('core:home')
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            return redirect('courses:course_list')
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {'form': form, 'title': 'Створити курс'})

@login_required
def course_update(request, slug):
    if request.user.role != 'admin':
        return redirect('core:home')
    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('courses:course_detail', slug=course.slug)
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/course_form.html', {'form': form, 'title': 'Редагувати курс'})

@login_required
def course_delete(request, slug):
    if request.user.role != 'admin':
        return redirect('core:home')
    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        course.delete()
        return redirect('courses:course_list')
    return render(request, 'courses/course_confirm_delete.html', {'course': course})

@login_required
def course_edit(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.user != course.teacher and request.user.role != 'admin':
        return redirect('core:home')
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('courses:course_edit', slug=course.slug)
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/course_edit.html', {'form': form, 'course': course})

@login_required
def module_create(request, course_slug):
    if request.user.role not in ['teacher', 'admin']:
        return redirect('core:home')
    course = get_object_or_404(Course, slug=course_slug)
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            return redirect('courses:course_detail', slug=course.slug)
    else:
        form = ModuleForm()
    return render(request, 'courses/module_form.html', {'form': form, 'title': 'Створити модуль'})

@login_required
def module_update(request, module_id):
    if request.user.role not in ['teacher', 'admin']:
        return redirect('core:home')
    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            return redirect('courses:course_detail', course_slug=module.course.slug)
    else:
        form = ModuleForm(instance=module)
    return render(request, 'courses/module_form.html', {'form': form, 'title': 'Редагувати модуль'})

@login_required
def module_delete(request, module_id):
    if request.user.role not in ['teacher', 'admin']:
        return redirect('core:home')
    module = get_object_or_404(Module, id=module_id)
    course_slug = module.course.slug
    if request.method == 'POST':
        module.delete()
        return redirect('courses:course_detail', slug=course_slug)
    return render(request, 'courses/module_confirm_delete.html', {'module': module})

@login_required
def lesson_create(request, module_id):
    if request.user.role not in ['teacher', 'admin']:
        return redirect('core:home')
    module = get_object_or_404(Module, id=module_id)
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            return redirect('courses:course_detail', course_slug=module.course.slug)
    else:
        form = LessonForm()
    return render(request, 'courses/lesson_form.html', {'form': form, 'title': 'Створити урок'})

@login_required
def lesson_update(request, lesson_id):
    if request.user.role not in ['teacher', 'admin']:
        return redirect('core:home')
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            return redirect('courses:course_detail', course_slug=lesson.module.course.slug)
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'courses/lesson_form.html', {'form': form, 'title': 'Редагувати урок'})

@login_required
def lesson_delete(request, lesson_id):
    if request.user.role not in ['teacher', 'admin']:
        return redirect('core:home')
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == 'POST':
        lesson.delete()
        return redirect('courses:course_detail', course_slug=lesson.module.course.slug)
    return render(request, 'courses/lesson_confirm_delete.html', {'lesson': lesson})

@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    submission = None
    
    if request.user.role == 'student':
        submission = StudentSubmission.objects.filter(student=request.user, lesson=lesson).first()
    
    if request.method == 'POST' and request.user.role == 'student':
        submission_url = request.POST.get('submission_url')
        if submission_url:
            StudentSubmission.objects.update_or_create(
                student=request.user,
                lesson=lesson,
                defaults={'submission_url': submission_url}
            )
            messages.success(request, 'Роботу успішно здано!')
            return redirect('courses:lesson_detail', lesson_id=lesson.id)
    
    context = {
        'lesson': lesson,
        'submission': submission,
    }
    return render(request, 'courses/lesson_detail.html', context)

@login_required
def student_home(request):
    student_courses = Course.objects.filter(students=request.user)
    return render(request, 'courses/home.html', {'student_courses': student_courses})

@login_required
def course_detail_view(request, slug):
    course = get_object_or_404(Course, slug=slug)
    modules = course.modules.all().order_by('order')
    messages.get_messages(request)
    submitted_assignments_data = StudentAssignmentSubmission.objects.filter(
        student=request.user, 
        lesson__module__course=course
    ).select_related('lesson')
    
    submitted_assignments_ids = [sub.lesson.id for sub in submitted_assignments_data]
    submissions_by_lesson = {sub.lesson.id: sub for sub in submitted_assignments_data}

    average_grade = None
    has_certificate = StudentAssignmentSubmission.objects.filter(
        student=request.user, 
        lesson__module__course=course, 
        certificate_issued=True
    ).exists()
    
    graded_submissions = submitted_assignments_data.exclude(grade__isnull=True)
    if graded_submissions:
        total_grade = sum(sub.grade for sub in graded_submissions)
        average_grade = total_grade / len(graded_submissions)

    context = {
        'course': course,
        'modules': modules,
        'submitted_assignments': submitted_assignments_ids,
        'submissions_by_lesson': submissions_by_lesson,
        'average_grade': average_grade,
        'has_certificate': has_certificate,
    }
    return render(request, 'courses/course_detail.html', context)

@login_required
def download_certificate(request, course_slug):
    """Генерує та віддає HTML сертифікат для завантаження."""
    course = get_object_or_404(Course, slug=course_slug)
    has_certificate = StudentAssignmentSubmission.objects.filter(
        student=request.user, 
        lesson__module__course=course, 
        certificate_issued=True
    ).exists()

    if not has_certificate:
        messages.error(request, "Сертифікат для цього курсу ще не видано.")
        return redirect('courses:course_detail', slug=course_slug)

    certificate_html = generate_certificate_html(request.user, course)
    response = HttpResponse(certificate_html, content_type='text/html; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="certificate_{course.slug}_{request.user.username}.html"'
    return response

def home_view(request):
    from django.http import HttpResponse
    announcements = Announcement.objects.all()
    debug = f"DEBUG: announcements.count = {announcements.count()}\n"
    for a in announcements:
        debug += f"ID={a.id}, title={a.title}, author={a.author}, date={a.publication_date}\n"
    return HttpResponse(f'<pre>{debug}</pre>')
#    events = Event.objects.filter(date__gte=datetime.date.today())[:5]
#    new_courses = Course.objects.order_by('-created_at')[:5]
#    context = {
#        'announcements': announcements,
#        'events': events,
#        'new_courses': new_courses,
#    }
#    return render(request, 'home.html', context)

def course_list_view(request):
    courses = Course.objects.all()
    announcements = Announcement.objects.all().order_by('-publication_date')[:5]
    new_courses = Course.objects.order_by('-created_at')[:5]
    context = {
        'courses': courses,
        'announcements': announcements,
        'new_courses': new_courses,
    }
    return render(request, 'courses/home.html', context)
