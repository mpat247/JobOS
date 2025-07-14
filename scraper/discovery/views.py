import json
import platform
import socket
import django

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.db import connection
from django.middleware.csrf import get_token
from celery import chain
from discovery.tasks import search_normalize_task, crawl_career_pages_task
from logging_config import setup_logging

logger = setup_logging()

@csrf_exempt
@require_POST
def add_company(request):
    logger.info("[add_company] Received request to add company")
    data = json.loads(request.body)
    logger.debug(f"[add_company] Request data: {data}")

    company = data.get("company", "").strip()
    country = data.get("country", "").strip()
    if not company or not country:
        logger.warning("[add_company] Missing 'company' or 'country' in request")
        return JsonResponse({"error": "Missing 'company' or 'country'"}, status=400)

    logger.info(f"[add_company] Queuing tasks for company: {company}, country: {country}")
    # Stage 1 (normalize URLs) → Stage 2 (crawl URLs)
    chain(
        search_normalize_task.s(company, country),
        crawl_career_pages_task.s(company, country)
    ).apply_async()

    return JsonResponse({"status": "queued"}, status=202)


def healthCheckView(request):
    logger.info("[healthCheckView] Performing health check")
    try:
        connection.ensure_connection()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        logger.error(f"[healthCheckView] Database connection error: {e}")

    csrf_token = get_token(request)

    logger.debug(f"[healthCheckView] CSRF token: {csrf_token}")

    return JsonResponse({
        "status": "ok",
        "time": now().isoformat(),
        "server": socket.gethostname(),
        "system": platform.system(),
        "python_version": platform.python_version(),
        "django_version": django.get_version(),
        "database": db_status,
        "csrf_token": csrf_token
    })
