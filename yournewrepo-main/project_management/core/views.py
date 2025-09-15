from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from .models import Faculty, Student, Project

def home(request):
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    if hasattr(request.user, 'faculty'):
        return faculty_dashboard(request)
    elif hasattr(request.user, 'student'):
        return student_dashboard(request)
    else:
        messages.error(request, "Account type not recognized.")
        return redirect('home')
    
def logout_view(request):
    logout(request)
    messages.success(request, "Successfully logged out!")
    return redirect('home')

@login_required
def faculty_dashboard(request):
    if not hasattr(request.user, 'faculty'):
        messages.error(request, "You don't have faculty permissions.")
        return redirect('home')
    
    faculty = request.user.faculty
    students = Student.objects.filter(faculty=faculty).order_by('batch')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, "Both username and password are required.")
            return redirect('dashboard')
        
        try:
            # Check if username exists
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
                return redirect('dashboard')
            
            # Create the user account
            user = User.objects.create_user(
                username=username,
                password=password,
                is_active=True
            )
            
            # Create the student object with the same batch as faculty
            student = Student.objects.create(
                user=user,
                faculty=faculty,
                batch=faculty.batch  # Inherit batch from faculty
            )
            
            # Add to student group
            student_group, _ = Group.objects.get_or_create(name='Student')
            user.groups.add(student_group)
            user.save()
            
            messages.success(request, f"Student account '{username}' created successfully!")
            
        except Exception as e:
            print(f"Error creating student: {str(e)}")
            messages.error(request, "Error creating student account.")
            if user:
                user.delete()
                
        return redirect('dashboard')
    
    return render(request, 'core/faculty_dashboard.html', {
        'students': students
    })
    
@login_required
def student_dashboard(request):
    if not hasattr(request.user, 'student'):
        messages.error(request, "You don't have student permissions.")
        return redirect('home')
    
    student = request.user.student
    projects = Project.objects.filter(student=student).order_by('-created_at')
    
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')
            video = request.FILES.get('video')
            
            if not title or not description or not video:
                messages.error(request, "Title, description and video are all required.")
                return redirect('dashboard')
            
            # Create new project
            Project.objects.create(
                student=student,
                title=title,
                description=description,
                video=video
            )
            
            messages.success(request, "Project uploaded successfully!")
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f"Error uploading project: {str(e)}")
            return redirect('dashboard')
    
    return render(request, 'core/student_dashboard.html', {
        'projects': projects
    })
    
    
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

def department_selection(request):
    departments = Faculty.DEPARTMENT_CHOICES
    return render(request, 'core/department_selection.html', {
        'departments': departments
    })

def department_projects(request, department_code):
    department_name = dict(Faculty.DEPARTMENT_CHOICES)[department_code]
    projects = Project.objects.filter(
        student__faculty__department=department_code
    ).select_related('student', 'student__user').order_by('student__batch', '-created_at')
    
    return render(request, 'core/department_projects.html', {
        'department_name': department_name,
        'projects': projects
    })

@login_required
def delete_project(request, project_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, id=project_id, student=request.user.student)
        project.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)

@login_required
def student_dashboard(request):
    if not hasattr(request.user, 'student'):
        messages.error(request, "You don't have student permissions.")
        return redirect('home')
    
    student = request.user.student
    projects = Project.objects.filter(student=student).order_by('-created_at')
    
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            description = request.POST.get('description')
            group_members = request.POST.get('group_members')  # New field
            video = request.FILES.get('video')
            
            if not all([title, description, group_members, video]):
                messages.error(request, "All fields are required.")
                return redirect('dashboard')
            
            # Create new project
            Project.objects.create(
                student=student,
                title=title,
                description=description,
                group_members=group_members,  # Add group members
                video=video
            )
            
            messages.success(request, "Project uploaded successfully!")
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f"Error uploading project: {str(e)}")
            return redirect('dashboard')
    
    return render(request, 'core/student_dashboard.html', {
        'projects': projects
    })