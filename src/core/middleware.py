import logging
from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import HttpResponseForbidden
from src.core.application.exceptions import PermissionDeniedError
from src.core.infrastructure.exceptions import NotFoundError

logger = logging.getLogger(__name__)


class ExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        logger.exception(f"Exception occurred: {exception}")

        if isinstance(exception, NotFoundError):
            return render(request, 'error/not_found.html', {
                'message': str(exception)
            }, status=404)

        elif isinstance(exception, PermissionDeniedError):
            return render(request, 'error/permission_denied.html', {
                'message': str(exception)
            }, status=403)

        messages.error(request, "An unexpected error occurred. Please try again later.")
        return redirect('home')  # Redirect to your home page