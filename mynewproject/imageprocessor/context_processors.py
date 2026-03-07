from django.conf import settings


def kimi_settings(request):
    """Global context processor for Kimi API settings"""
    return {
        'KIMI_API_KEY': getattr(settings, 'KIMI_API_KEY', ''),
        'KIMI_API_BASE_URL': getattr(settings, 'KIMI_API_BASE_URL', ''),
    }