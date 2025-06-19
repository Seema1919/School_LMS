from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout

from django.http import HttpResponse
from .forms import CustomUserCreationForm
from .models import  CustomUser


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import StudentForm, SubjectFormSet, TaskForm
from .models import Student, Subject, Task

User = CustomUser

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        return render(request, 'schoolapp/register.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    return render(request, 'schoolapp/register.html', {'form': form})

def login_view(request):
    error_message = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            error_message = 'Invalid email or password'
            return render(request, 'schoolapp/login.html', {'error_message': error_message})

        user = authenticate(request, username=user_obj.username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            error_message = 'Invalid email or password'
    return render(request, 'schoolapp/login.html', {'error_message': error_message})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    if request.user.user_type == 'teacher':
        return render(request, 'schoolapp/dashboard.html', {'user': request.user, 'user_type': 'teacher'})

    elif request.user.user_type == 'student':
        try:
            student = Student.objects.get(user=request.user)
            tasks = Task.objects.filter(student=student)
            return render(request, 'schoolapp/student_dashboard.html', {
                'user': request.user,
                'user_type': 'student',
                'student': student,
                'tasks': tasks
            })
        except Student.DoesNotExist:
            return render(request, 'schoolapp/error.html', {
                'message': "Student record not found. Please contact admin or your teacher."
            })

    return HttpResponse("Unauthorized", status=401)

@login_required
def add_student_view(request):
    student_form = StudentForm()
    subject_formset = SubjectFormSet()
    task_form = TaskForm()

    show_student_form = False
    show_task_form = False

    if request.method == 'POST':
        if 'show_student_form' in request.POST:
            show_student_form = True

        elif 'show_task_form' in request.POST:
            show_task_form = True

        elif 'submit_student' in request.POST:
            student_form = StudentForm(request.POST)
            subject_formset = SubjectFormSet(request.POST)
            show_student_form = True
            if student_form.is_valid() and subject_formset.is_valid():
                student = student_form.save(commit=False)
                student.user = request.user
                student.save()
                subjects = subject_formset.save(commit=False)
                for subject in subjects:
                    subject.student = student
                    subject.save()
                return redirect('add_student')

        elif 'submit_task' in request.POST:
            task_form = TaskForm(request.POST)
            show_task_form = True
            if task_form.is_valid():
                student_id = request.POST.get('student_id')
                student = get_object_or_404(Student, id=student_id, user=request.user)
                task = task_form.save(commit=False)
                task.student = student
                task.save()
                return redirect('add_student')

    students = Student.objects.filter(user=request.user).prefetch_related('subjects', 'task_set')
    return render(request, 'schoolapp/add_student.html', {
        'student_form': student_form,
        'subject_formset': subject_formset,
        'task_form': task_form,
        'students': students,
        'show_student_form': show_student_form,
        'show_task_form': show_task_form
    })


@login_required
def dashboard_view(request):
    return render(request, 'schoolapp/dashboard.html', {
        'user': request.user,
        'user_type': request.user.user_type,
    })


