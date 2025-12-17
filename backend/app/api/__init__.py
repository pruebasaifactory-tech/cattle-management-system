"""API routers package."""
from .auth import router as auth_router
from .cattle import router as cattle_router

__all__ = ["auth_router", "cattle_router"]
