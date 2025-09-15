from django.contrib import admin
from .models import Faculty, Student, Project

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'faculty')
    list_filter = ('faculty',)
    search_fields = ('user__username',)

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'phone')
    search_fields = ('user__username', 'department')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('student', 'description', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('student__user__username', 'description')
    

#SEARCH FIELDS are basically field using which we can search in admin panel
#user__ means we are using built in user model of django and calling username from it

#'created at' is a datetimefield and when django sees this field ti creates filtering options based on that