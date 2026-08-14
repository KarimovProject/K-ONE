from django.conf import settings


class ProductionSecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.setdefault("Referrer-Policy", settings.SECURE_REFERRER_POLICY)
        response.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; "
            "base-uri 'self'; frame-ancestors 'none'; object-src 'none'; "
            "img-src 'self' data:; font-src 'self' https://fonts.gstatic.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net "
            "https://fonts.googleapis.com; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "connect-src 'self'; form-action 'self'",
        )
        if request.path.startswith(("/event/", "/api/v1/public/", "/display/")):
            response["Cache-Control"] = "private, no-store, max-age=0"
        return response
