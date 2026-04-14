from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project
from participation.models import Participation


@login_required
def dashboard(request):
    projects = Project.objects.all()
    return render(request, 'dashboard.html', {'projects': projects})


@login_required
def create_project(request):

    if request.user.role != 'leader':
        return redirect('dashboard')

    if request.method == 'POST':
        Project.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            location=request.POST.get('location'),
            category=request.POST.get('category'),
            leader=request.user
        )
        return redirect('dashboard')

    return render(request, 'create_project.html')


@login_required
def project_detail(request, project_id):

    project = get_object_or_404(Project, id=project_id)
    participants = Participation.objects.filter(project=project)

    return render(request, 'project_detail.html', {
        'project': project,
        'participants': participants
    })


@login_required
def join_project(request, project_id):

    project = get_object_or_404(Project, id=project_id)

    already = Participation.objects.filter(
        user=request.user,
        project=project
    ).exists()

    if not already:
        Participation.objects.create(user=request.user, project=project)

    return redirect('project_detail', project_id=project.id)