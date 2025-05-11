from django.template.loader import render_to_string
from assignments.models import StudentAssignmentSubmission
from django.utils import timezone

def generate_certificate_html(student, course):
    """Генерує HTML-код сертифіката для студента та курсу."""
    submissions = StudentAssignmentSubmission.objects.filter(
        student=student, lesson__module__course=course
    ).exclude(grade__isnull=True)
    if submissions:
        total_grade = sum(submission.grade for submission in submissions)
        average_grade = total_grade / len(submissions)
    else:
        average_grade = 0

    context = {
        'student_full_name': f"{student.first_name} {student.last_name}",
        'course_full_name': course.title,
        'instructor_full_name': f"{course.teacher.first_name} {course.teacher.last_name}" if course.teacher else "_________________________",
        'average_grade': f"{average_grade:.2f}",
        'current_date': timezone.now().strftime("%d.%m.%Y"),
        'specialty': "ІТ",
        'faculty': "LMS",
        'university': "LMS",
    }
    return render_to_string('courses/certificate_template.html', context) 