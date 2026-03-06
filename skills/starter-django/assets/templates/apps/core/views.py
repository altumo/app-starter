from django.db import connection
from django.http import JsonResponse


def health_check(request):
    """Health check endpoint for load balancers and monitoring."""
    health = {"status": "healthy", "checks": {}}

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health["checks"]["database"] = "ok"
    except Exception:
        health["status"] = "unhealthy"
        health["checks"]["database"] = "unavailable"

    status_code = 200 if health["status"] == "healthy" else 503
    return JsonResponse(health, status=status_code)
