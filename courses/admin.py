from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect
from django.contrib import messages
from .models import Course, Module, Lesson, StudentSubmission, Announcement, Event
from users.models import CustomUser
from django.utils.html import format_html
from assignments.models import StudentAssignmentSubmission

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

class StudentSubmissionInline(admin.TabularInline):
    model = StudentSubmission
    extra = 0
    readonly_fields = ('student', 'submitted_at', 'updated_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'teacher')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('is_published',)
    search_fields = ('title', 'description')
    inlines = [ModuleInline]
    filter_horizontal = ('students',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('issue_certificates/<int:course_id>/', self.admin_site.admin_view(self.issue_certificates), name='issue_certificates'),
        ]
        return custom_urls + urls

    def issue_certificates(self, request, course_id):
        course = self.model.objects.get(pk=course_id)
        students = CustomUser.objects.filter(assignment_submissions__lesson__module__course=course).distinct()
        issued_count = 0

        for student in students:
            submissions = StudentAssignmentSubmission.objects.filter(
                student=student, 
                lesson__module__course=course
            ).exclude(grade__isnull=True)
            
            if submissions:
                total_grade = sum(sub.grade for sub in submissions)
                average_grade = total_grade / len(submissions)
                if average_grade > 3:
                    StudentAssignmentSubmission.objects.filter(
                        student=student, 
                        lesson__module__course=course
                    ).update(certificate_issued=True)
                    issued_count += 1

        messages.success(request, f"Сертифікати видано для {issued_count} студентів курсу '{course.title}'.")
        return redirect('admin:courses_course_change', course_id)

    def issue_certificates_button(self, obj):
        return format_html(
            '<a class="button" href="{}">Видати сертифікати</a>',
            reverse('admin:issue_certificates', args=[obj.id])
        )
    issue_certificates_button.short_description = 'Сертифікати'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)
        if obj:
            extra_context['issue_certificates_button'] = self.issue_certificates_button(obj)
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def teacher_link(self, obj):
        if obj.teacher:
            return format_html("<a href='{}'>{}</a>",
                                f'/admin/users/customuser/{obj.teacher.id}/change/',
                                obj.teacher.get_full_name())
        return "Не призначено"
    teacher_link.short_description = 'Викладач'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(teacher=request.user)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        return ('teacher', 'created_at', 'updated_at')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'teacher' and not request.user.is_superuser:
            kwargs['initial'] = request.user
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'students' and not request.user.is_superuser:
            kwargs['queryset'] = CustomUser.objects.filter(role='student')
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.teacher = request.user
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'description')
    inlines = [LessonInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(course__teacher=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'course' and not request.user.is_superuser:
            kwargs['queryset'] = Course.objects.filter(teacher=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order', 'has_lecture', 'has_submission_field')
    list_filter = ('module__course',)
    search_fields = ('title', 'content', 'lecture_url', 'submission_url_field_name')
    inlines = [StudentSubmissionInline]
    fieldsets = (
        ('Основна інформація', {
            'fields': ('module', 'title', 'content', 'order')
        }),
        ('Медіа', {
            'fields': ('video_url', 'lecture_url', 'lecture_files', 'assignment_files')
        }),
        ('Завдання', {
            'fields': ('assignment_description', 'assignment_due_date', 'submission_url_field_name')
        }),
    )

    def has_lecture(self, obj):
        return bool(obj.lecture_url)
    has_lecture.boolean = True
    has_lecture.short_description = 'Є лекція'

    def has_submission_field(self, obj):
        return bool(obj.submission_url_field_name)
    has_submission_field.boolean = True
    has_submission_field.short_description = 'Є поле для здачі'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(module__course__teacher=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'module' and not request.user.is_superuser:
            kwargs['queryset'] = Module.objects.filter(course__teacher=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class StudentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'submitted_at', 'updated_at', 'submission_link')
    list_filter = ('lesson__module__course', 'lesson')
    search_fields = ('student__email', 'student__first_name', 'student__last_name', 'submission_url')
    readonly_fields = ('submitted_at', 'updated_at')

    def submission_link(self, obj):
        return format_html("<a href='{}' target='_blank'>Відкрити роботу</a>", obj.submission_url)
    submission_link.short_description = 'Посилання на роботу'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(lesson__module__course__teacher=request.user)

class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_date', 'category')
    list_filter = ('author', 'publication_date', 'category')
    search_fields = ('title', 'text')

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'location')
    list_filter = ('date', 'time')
    search_fields = ('title', 'description', 'location')

admin.site.register(Course, CourseAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(StudentSubmission, StudentSubmissionAdmin)
admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(Event, EventAdmin)
