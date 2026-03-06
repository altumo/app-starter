from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def home(request):
    """Public home page."""
    return render(request, "pages/home.html")


@login_required
def dashboard(request):
    """Protected dashboard page. Requires authentication."""
    return render(request, "pages/dashboard.html")
