from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings


def _key_func(request):
    return get_remote_address(request)


limiter = Limiter(key_func=_key_func, enabled=settings.rate_limit_enabled)
