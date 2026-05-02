from django.shortcuts import redirect


class RoleAccessMiddleware:
    """
    Basic role-based route protection
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # SAFE GUARD (FIX CRASH)
        user = getattr(request, "user", None)

        if not user or not hasattr(user, "is_authenticated"):
            return self.get_response(request)

        path = request.path

        # allow admin routes
        if path.startswith("/admin/"):
            return self.get_response(request)

        # optional protected route groups
        protected_routes = ["/leader/", "/volunteer/", "/tasks/"]

        if any(path.startswith(r) for r in protected_routes):
            if not user.is_authenticated:
                return redirect("login")

        return self.get_response(request)