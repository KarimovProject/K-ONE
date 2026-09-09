import json
import logging
from datetime import datetime
from django.conf import settings
from pathlib import Path

# Set up a dedicated logger for admin audit
AUDIT_LOG_FILE = getattr(settings, "BASE_DIR", Path(".")) / "logs" / "admin_audit.log"
AUDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

audit_logger = logging.getLogger("admin_audit")
audit_logger.setLevel(logging.INFO)
handler = logging.FileHandler(AUDIT_LOG_FILE, encoding="utf-8")
handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
audit_logger.addHandler(handler)
audit_logger.propagate = False

class AdminAuditLogMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated and request.method in ("POST", "PUT", "DELETE", "PATCH"):
            path = request.path
            
            user_info = f"{request.user.username} ({request.user.role})"
            log_msg = f"User: {user_info} | Method: {request.method} | Path: {path} | Status: {response.status_code}"
            
            audit_logger.info(log_msg)

        return response
