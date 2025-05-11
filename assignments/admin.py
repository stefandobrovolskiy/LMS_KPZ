from django.contrib import admin
from .models import Assignment, StudentAssignmentSubmission

class StudentAssignmentSubmissionInline(admin.TabularInline):
    model = StudentAssignmentSubmission
    extra = 0
    readonly_fields = ('student', 'submission_url', 'upload_file', 'submitted_at')
    can_delete = False

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'due_date')
    list_filter = ('lesson', 'due_date')
    search_fields = ('title', 'description')
    inlines = [StudentAssignmentSubmissionInline]

class StudentAssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'lesson', 'submitted_at', 'grade')
    list_filter = ('lesson', 'assignment', 'student', 'submitted_at', 'grade')
    search_fields = ('student__username', 'lesson__title', 'assignment__title')
    readonly_fields = ('student', 'assignment', 'lesson', 'submitted_at', 'submission_url', 'upload_file')
    fieldsets = (
        (None, {
            'fields': ('student', 'assignment', 'lesson', 'submitted_at', 'submission_url', 'upload_file')
        }),
        ('Оцінювання', {
            'fields': ('grade', 'feedback')
        }),
    )

admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(StudentAssignmentSubmission, StudentAssignmentSubmissionAdmin)
