import pyotp
from .models import  CustomUser
from django.contrib.auth.decorators import login_required
from .forms import StudentForm, SubjectFormSet, TaskForm
from .models import Student, Subject, Task
from django.forms.models import inlineformset_factory
from .forms import CustomUserCreationForm
from .models import OtpToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout


@login_required
def dashboard_view(request):
    return render(request, 'schoolapp/dashboard.html', {
        'user': request.user,
        'user_type': request.user.user_type,
    })

#register


def register(request):
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! An OTP was sent to your Email")
            return redirect("verify_email", username=request.POST['username'])
    context = {"form": form}
    return render(request, "schoolapp/register.html", context)


def verify_email(request, username):
    user = get_user_model().objects.get(username=username)
    user_otp = OtpToken.objects.filter(user=user).last()

    if request.method == 'POST':
        # valid token
        if user_otp.otp_code == request.POST['otp_code']:

            # checking for expired token
            if user_otp.otp_expires_at > timezone.now():
                user.is_active = True
                user.save()
                messages.success(request, "Account activated successfully!! You can Login.")
                return redirect("register")

            # expired token
            else:
                messages.warning(request, "The OTP has expired, get a new OTP!")
                return redirect("verify_email", username=user.username)


        # invalid otp code
        else:
            messages.warning(request, "Invalid OTP entered, enter a valid OTP!")
            return redirect("verify_email", username=user.username)

    context = {}
    return render(request, "schoolapp/verify_email.html", context)


def resend_otp(request):
    if request.method == 'POST':
        user_email = request.POST["otp_email"]

        if get_user_model().objects.filter(email=user_email).exists():
            user = get_user_model().objects.get(email=user_email)
            otp = OtpToken.objects.create(user=user, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5))

            # email variables
            subject = "Email Verification"
            message = f"""
                                Hi {user.username}, here is your OTP {otp.otp_code} 
                                it expires in 5 minute, use the url below to redirect back to the website
                                http://127.0.0.1:8000/verify_email/{user.username}

                                """
            sender = "clintonmatics@gmail.com"
            receiver = [user.email, ]

            # send email
            send_mail(
                subject,
                message,
                sender,
                receiver,
                fail_silently=False,
            )

            messages.success(request, "A new OTP has been sent to your email-address")
            return redirect("verify_email", username=user.username)

        else:
            messages.warning(request, "This email dosen't exist in the database")
            return redirect("resend_otp")

    context = {}
    return render(request, "schoolapp/resend_otp.html", context)


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Hi {request.user.username}, you are now logged-in")
            return redirect("dashboard")

        else:
            messages.warning(request, "Invalid credentials")
            return redirect("signin")

    return render(request, "schoolapp/login.html")


#dashborad_view
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

    return redirect('login')



# edit student
@login_required
def edit_student_view(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    form = StudentForm(request.POST or None, instance=student)
    if form.is_valid():
        form.save()
        messages.success(request, 'Student updated.')
        return redirect('dashboard')
    return render(request, 'schoolapp/edit_student.html', {'form': form})



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

    if request.method == 'GET':
        if 'show_student_form' in request.GET:
            show_student_form = True
        elif 'show_task_form' in request.GET:
            show_task_form = True


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

    #  Always show students created by this user
    students = Student.objects.filter(created_by=request.user).prefetch_related('subjects', 'tasks')

    return render(request, 'schoolapp/add_student.html', {
        'student_form': student_form,
        'subject_formset': subject_formset,
        'task_form': task_form,
        'students': students,
        'show_student_form': show_student_form,
        'show_task_form': show_task_form,
    })



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

def verify_otp(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        user_id = request.session.get('otp_user_id')
        user = get_object_or_404(CustomUser, id=user_id)

        totp = pyotp.TOTP(user.totp_secret)
        if totp.verify(otp_entered):
            user.is_active = True
            user.save()
            messages.success(request, "Account verified. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP. Try again.")

    return render(request, 'schoolapp/verify_email.html')

