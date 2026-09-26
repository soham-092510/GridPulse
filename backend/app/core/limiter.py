from slowapi import Limiter
from slowapi.util import get_remote_address

# Global IP-based rate limiter
# Default limit: 120 requests/minute per client IP (protects API from DDoS/abuse while keeping dashboard smooth)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120/minute"]
)
