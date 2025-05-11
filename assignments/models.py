from django.db import models
from courses.models import Course, Lesson
from users.models import CustomUser

# Create your models here.

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assignments')
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class StudentAssignmentSubmission(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assignment_submissions')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assignment_submissions', null=True)
    submission_url = models.URLField(blank=True, null=True)
    upload_file = models.FileField(upload_to='submissions/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.IntegerField(blank=True, null=True, verbose_name='Оцінка')
    feedback = models.TextField(blank=True, verbose_name='Коментар викладача')
    certificate_issued = models.BooleanField(default=False, verbose_name='Сертифікат видано')

    class Meta:
        unique_together = ('student', 'lesson')

    def save(self, *args, **kwargs):
        if not self.lesson and self.assignment:
            self.lesson = self.assignment.lesson
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Робота {self.student.get_full_name()} для {self.lesson.title if self.lesson else 'Невідомий урок'}"
