from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Job, Application

# 🔍 Home Page with Search + Filters
def home(request):
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    skills = request.GET.get('skills', '')

    jobs = Job.objects.all()

    if query:
        jobs = jobs.filter(
            title__icontains=query
        ) | jobs.filter(
            location__icontains=query
        ) | jobs.filter(
            description__icontains=query
        )

    if location:
        jobs = jobs.filter(location__icontains=location)

    if skills:
        jobs = jobs.filter(skills__icontains=skills)

    jobs = jobs.order_by('-posted_at')

    # Dropdown values
    locations = Job.objects.values_list('location', flat=True).distinct()
    skills_list = Job.objects.values_list('skills', flat=True).distinct()

    # Applied job IDs for logged-in user
    applied_job_ids = []
    if request.user.is_authenticated:
        applied_job_ids = Application.objects.filter(user=request.user).values_list('job_id', flat=True)

    return render(request, 'core/home.html', {
        'jobs': jobs,
        'query': query,
        'selected_location': location,
        'selected_skills': skills,
        'locations': locations,
        'skills_list': skills_list,
        'applied_job_ids': applied_job_ids,
    })

# 📝 Signup View
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')
        user = User.objects.create_user(username=username, password=password)
        messages.success(request, "User created successfully!")
        return redirect('login')
    return render(request, 'core/signup.html')

# 🔐 Login View
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')
    return render(request, 'core/login.html')

# 🚪 Logout
def logout_view(request):
    logout(request)
    return redirect('home')

# 📤 Apply to Job (resume required)
@login_required
def apply_job(request, job_id):
    job = Job.objects.get(id=job_id)
    already_applied = Application.objects.filter(user=request.user, job=job).exists()

    if already_applied:
        messages.info(request, "You have already applied for this job.")
    else:
        if request.method == 'POST':
            resume = request.FILES.get('resume')
            if not resume:
                messages.error(request, "Please upload your resume.")
                return redirect('home')

            Application.objects.create(user=request.user, job=job, resume=resume)
            messages.success(request, "Application submitted successfully.")
    return redirect('home')

# 📄 My Applications (shows resume link)
@login_required
def my_applications(request):
    applications = Application.objects.filter(user=request.user).select_related('job').order_by('-applied_at')
    return render(request, 'core/my_applications.html', {
        'applications': applications
    })

# 🙍‍♂️ Profile Page (latest uploaded resume preview)
@login_required
def profile(request):
    latest_resume = Application.objects.filter(user=request.user, resume__isnull=False).order_by('-applied_at').first()
    return render(request, 'core/profile.html', {
        'latest_resume': latest_resume
    })
