from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from django.http import HttpResponse
from .forms import StudentForm, TaskForm

User = get_user_model()


# Register View
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  #
        else:

            return render(request, 'schoolapp/register.html', {'form': form})
    else:
        form = CustomUserCreationForm()
        return render(request, 'schoolapp/register.html', {'form': form})




# Login View using Email
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

    return render(request, 'schoolapp/login.html')


# Dashboard View based on user_type
@login_required
def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    return render(request, 'schoolapp/dashboard.html', {
        'user': request.user,
        'user_type': request.user.user_type
    })


# Logout View
def logout_view(request):
    logout(request)
    return redirect('login')


# Redirect from / to /register
def redirect_to_register(request):
    return redirect('register')


# Unused home view (you can remove this if not using)
@login_required
def home(request):
    return render(request, 'schoolapp/dashboard.html')


# Add Student Form (Teacher Access)
@login_required
def add_student(request):
    if request.user.user_type != 'teacher':
        return HttpResponse("Unauthorized", status=401)
    return render(request, 'schoolapp/add_student.html')

def add_student_view(request):
    student_form = StudentForm()
    task_form = TaskForm()

    if request.method == 'POST':
        if 'submit_student' in request.POST:
            student_form = StudentForm(request.POST)
            if student_form.is_valid():
                student_form.save()
                return redirect('h')

        elif 'submit_task' in request.POST:
            task_form = TaskForm(request.POST)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.assigned_by = request.user
                task.save()
                return redirect('home')

    context = {
        'student_form': student_form,
        'task_form': task_form,
    }
    return render(request, 'schoolapp/add_student.html', context)
