from django.shortcuts import redirect
from functools import wraps


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if not (request.user.is_superuser or request.user.role == "admin"):
            return redirect("home")

        return view_func(request, *args, **kwargs)

    return wrapper


def leader_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.role != "leader" and not request.user.is_superuser:
            return redirect("home")

        return view_func(request, *args, **kwargs)

    return wrapper


def volunteer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.role != "volunteer" and not request.user.is_superuser:
            return redirect("home")

        return view_func(request, *args, **kwargs)

    return wrapper