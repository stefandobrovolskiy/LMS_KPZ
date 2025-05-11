from django.db import models
from users.models import CustomUser
from django.utils.text import slugify

# Create your models here.

class Course(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='courses_taught')
    is_published = models.BooleanField(default=False)
    image = models.ImageField(upload_to='courses/', blank=True, null=True)
    students = models.ManyToManyField(CustomUser, related_name='courses_enrolled', blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Module(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['order']

class Lesson(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField()
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    video_url = models.URLField(blank=True, null=True)
    lecture_url = models.URLField(blank=True, null=True, help_text="Посилання на лекцію в Google Drive")
    submission_url_field_name = models.CharField(max_length=200, blank=True, null=True, help_text="Назва поля для посилання на роботу студента")
    assignment_file_field_name = models.CharField(max_length=200, blank=True, null=True, help_text="Назва поля для завантаження файлу роботи студента")
    
    # Поля для файлів
    lecture_files = models.FileField(upload_to='lectures/%Y/%m/%d/', blank=True, null=True)
    assignment_files = models.FileField(upload_to='assignments/%Y/%m/%d/', blank=True, null=True)
    assignment_description = models.TextField(blank=True, null=True)
    assignment_due_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['order']

class StudentSubmission(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='submissions')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='submissions')
    submission_url = models.URLField(help_text="Посилання на роботу в Google Drive")
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'lesson')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Робота {self.student.get_full_name()} для {self.lesson.title}"

class Announcement(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст")
    author = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, verbose_name="Автор")
    publication_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публікації")
    category = models.CharField(max_length=100, blank=True, null=True, verbose_name="Категорія")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-publication_date']

class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name="Назва")
    description = models.TextField(verbose_name="Опис")
    date = models.DateField(verbose_name="Дата")
    time = models.TimeField(verbose_name="Час")
    location = models.CharField(max_length=200, verbose_name="Місце проведення")
    image = models.ImageField(upload_to='events/', blank=True, null=True, verbose_name="Зображення")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['date', 'time']
