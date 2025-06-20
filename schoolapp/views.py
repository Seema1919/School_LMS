from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.http import HttpResponse
from .forms import CustomUserCreationForm
from .models import  CustomUser
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import StudentForm, SubjectFormSet, TaskForm
from .models import Student, Subject, Task

User = CustomUser
from django.shortcuts import get_object_or_404
from django.contrib import messages

def verify_otp_view(request):
    if request.method == 'POST':
        user_id = request.session.get('otp_user_id')
        user = get_object_or_404(CustomUser, id=user_id)

        entered_otp = request.POST.get('otp')
        totp = pyotp.TOTP(user.totp_secret)

        if totp.verify(entered_otp):
            user.is_active = True
            user.is_verified = True
            user.save()
            messages.success(request, "Account verified successfully!")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP. Try again.")

    return render(request, 'schoolapp/verify_otp.html')


@login_required
def dashboard_view(request):
    return render(request, 'schoolapp/dashboard.html', {
        'user': request.user,
        'user_type': request.user.user_type,
    })



from django.shortcuts import render, redirect
from django.core.mail import send_mail
import pyotp
from .models import CustomUser
from .forms import CustomUserCreationForm  # Use your custom form

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account until OTP verified
            user.totp_secret = pyotp.random_base32()  # Generate new secret
            user.save()

            # Generate OTP
            totp = pyotp.TOTP(user.totp_secret)
            otp_code = totp.now()

            # Send OTP to user email
            send_mail(
                'Your OTP Verification Code',
                f'Your verification code is: {otp_code}',
                'noreply@yourdomain.com',
                [user.email],
            )

            request.session['otp_user_id'] = user.id
            return redirect('verify_otp')  # You need to create this view and template
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



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Student, Task

@login_required
def dashboard_view(request):
    context = {
        'user': request.user,
        'user_type': request.user.user_type
    }

    if request.user.user_type == 'teacher':
        return render(request, 'schoolapp/dashboard.html', context)

    elif request.user.user_type == 'student':
        try:
            student = Student.objects.get(user=request.user)
            tasks = Task.objects.filter(student=student)
            context['student'] = student
            context['tasks'] = tasks
            return render(request, 'schoolapp/dashboard.html', context)
        except Student.DoesNotExist:
            messages.error(request, "Student record not found. Please contact your teacher.")
            return redirect('login')

    return redirect('login')  # For unknown user_type



@login_required
def edit_student_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    form = StudentForm(request.POST or None, instance=student)
    if form.is_valid():
        form.save()
        messages.success(request, 'Student updated.')
        return redirect('dashboard')
    return render(request, 'schoolapp/edit_student.html', {'form': form})


# Delete Student
@login_required
def delete_student_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    student.delete()
    messages.success(request, 'Student deleted.')
    return redirect('dashboard')


# Add Task
@login_required
def add_task_view(request):
    if request.user.user_type != 'teacher':
        return redirect('dashboard')

    form = TaskForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Task added.')
        return redirect('dashboard')
    return render(request, 'schoolapp/add_task.html', {'form': form})


# Edit Task
@login_required
def edit_student_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    SubjectFormSet = inlineformset_factory(Student, Subject, fields=('name', 'percentage'), extra=0, can_delete=True)

    if request.method == 'POST':
        student_form = StudentForm(request.POST, instance=student)
        formset = SubjectFormSet(request.POST, instance=student)

        if student_form.is_valid() and formset.is_valid():
            student_form.save()
            formset.save()
            messages.success(request, "Student updated successfully.")
            return redirect('dashboard')
    else:
        student_form = StudentForm(instance=student)
        formset = SubjectFormSet(instance=student)

    return render(request, 'schoolapp/edit_student.html', {
        'student_form': student_form,
        'subject_formset': formset,
    })


# Delete Task
@login_required
def delete_task_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    messages.success(request, 'Task deleted.')
    return redirect('dashboard')

@login_required
def add_student_view(request):
    student_form = StudentForm()
    subject_formset = SubjectFormSet()
    task_form = TaskForm()
    show_student_form = False
    show_task_form = False

    # ✅ Corrected GET method handling
    if request.method == 'GET':
        if 'show_student_form' in request.GET:
            show_student_form = True
        elif 'show_task_form' in request.GET:
            show_task_form = True

    # ✅ POST form submissions
    elif request.method == 'POST':
        if 'submit_student' in request.POST:
            student_form = StudentForm(request.POST)
            subject_formset = SubjectFormSet(request.POST)
            show_student_form = True  # Show form again if error

            if student_form.is_valid() and subject_formset.is_valid():
                student = student_form.save(commit=False)
                student.created_by = request.user
                student.save()
                subject_formset.instance = student
                subject_formset.save()
                messages.success(request, "Student and subjects added successfully.")
                return redirect('/add-student/?show_student_form=1')  # ✅ Keep form open

        elif 'submit_task' in request.POST:
            task_form = TaskForm(request.POST)
            show_task_form = True

            if task_form.is_valid():
                student_id = request.POST.get('student_id')
                try:
                    student = Student.objects.get(id=student_id, created_by=request.user)
                    task = task_form.save(commit=False)
                    task.student = student
                    task.save()
                    messages.success(request, "Task assigned successfully.")
                    return redirect('/add-student/?show_task_form=1')  # ✅ Keep form open
                except Student.DoesNotExist:
                    messages.error(request, "Selected student not found.")

    # ✅ Always show students created by this user
    students = Student.objects.filter(created_by=request.user).prefetch_related('subjects', 'tasks')

    return render(request, 'schoolapp/add_student.html', {
        'student_form': student_form,
        'subject_formset': subject_formset,
        'task_form': task_form,
        'students': students,
        'show_student_form': show_student_form,
        'show_task_form': show_task_form,
    })

from django.forms.models import inlineformset_factory


@login_required
def edit_task_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('add_student')  # or wherever you want to redirect after edit
    else:
        form = TaskForm(instance=task)

    return render(request, 'schoolapp/edit_task.html', {'form': form})
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

def verify_otp_view(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        user_id = request.session.get('otp_user_id')
        user = get_object_or_404(CustomUser, id=user_id)

        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(otp_entered):
            user.is_active = True
            user.save()
            del request.session['otp_user_id']  # ✅ Optional cleanup
            messages.success(request, "Account verified. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP. Try again.")

    return render(request, 'schoolapp/verify_otp.html')
