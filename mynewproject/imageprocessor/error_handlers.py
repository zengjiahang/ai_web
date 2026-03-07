from django.shortcuts import render
from django.http import HttpResponseServerError
import logging

logger = logging.getLogger(__name__)


def handler404(request, exception):
    """Custom 404 error handler"""
    logger.warning(f"404 error for {request.path}")
    return render(request, 'imageprocessor/error.html', {
        'error': 'Page not found',
        'error_code': 404
    }, status=404)


def handler500(request):
    """Custom 500 error handler"""
    logger.error(f"500 error for {request.path}")
    return render(request, 'imageprocessor/error.html', {
        'error': 'Internal server error',
        'error_code': 500
    }, status=500)


def handler403(request, exception):
    """Custom 403 error handler"""
    logger.warning(f"403 error for {request.path}")
    return render(request, 'imageprocessor/error.html', {
        'error': 'Access forbidden',
        'error_code': 403
    }, status=403)


def handler400(request, exception):
    """Custom 400 error handler"""
    logger.warning(f"400 error for {request.path}")
    return render(request, 'imageprocessor/error.html', {
        'error': 'Bad request',
        'error_code': 400
    }, status=400)