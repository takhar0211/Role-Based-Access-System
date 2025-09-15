from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver


class Faculty(models.Model):
    DEPARTMENT_CHOICES = [
        ('SE-IT-B', 'SE-IT-B'),
        ('SE-IT-A', 'SE-IT-A'),
    ]
    
    BATCH_CHOICES = [
        ('A', 'Batch A'),
        ('B', 'Batch B'),
        ('C', 'Batch C'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)
    phone = models.CharField(max_length=15)
    batch = models.CharField(max_length=1, choices=BATCH_CHOICES, default='A')

    class Meta:
        verbose_name_plural = "Faculties"

    def __str__(self):
        return f"{self.user.username} - {self.department} (Batch {self.batch})"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='students')
    batch = models.CharField(max_length=1, default='A')

    def __str__(self):
        return f"{self.user.username} - {self.faculty.department} (Batch {self.batch})"

class Project(models.Model):
    title = models.CharField(max_length=255)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='projects')
    description = models.TextField()
    group_members = models.TextField(help_text="Enter group members' names separated by commas")  # New field
    video = models.FileField(upload_to='project_videos/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['student__batch']

    def __str__(self):
        return f"{self.title} - {self.student.user.username}"

    def get_group_members_list(self):
        return [member.strip() for member in self.group_members.split(',') if member.strip()]
# Signal to ensure student group assignment
@receiver(post_save, sender=Student)
def create_student_group(sender, instance, created, **kwargs):
    if created:
        group, _ = Group.objects.get_or_create(name='Student')
        instance.user.groups.add(group)
        instance.user.save()

# Signal for faculty group assignment
@receiver(post_save, sender=Faculty)
def create_faculty_group(sender, instance, created, **kwargs):
    if created:
        group, _ = Group.objects.get_or_create(name='Faculty')
        instance.user.groups.add(group)
        instance.user.save()

#_ is for boolean