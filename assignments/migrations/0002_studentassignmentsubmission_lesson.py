# Generated by Django 5.2.1 on 2025-05-11 16:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0001_initial'),
        ('courses', '0006_lesson_lecture_url_lesson_submission_url_field_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentassignmentsubmission',
            name='lesson',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assignment_submissions', to='courses.lesson'),
        ),
    ]
