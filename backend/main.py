from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import assets, garments, health, jobs, tryon
from backend.core.config import Settings
from backend.core.errors import register_error_handlers
from backend.schemas.common import ErrorResponse
from backend.services.mock_provider import MockProvider
from backend.services.orchestrator import TryOnOrchestrator, TryOnProvider


def create_app(settings: Settings | None = None, provider: TryOnProvider | None = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(
        title="Virtual Try-On Platform API", version="0.1.0",
        description="MVP mock integration API. No image-based measurements or AI inference.",
        responses={status: {"model": ErrorResponse} for status in (400, 404, 413, 415, 422, 500)},
    )
    app.state.settings = settings
    app.state.orchestrator = TryOnOrchestrator(settings, provider or MockProvider(settings.asset_dir))
    app.add_middleware(
        CORSMiddleware, allow_origins=list(settings.cors_origins), allow_credentials=False,
        allow_methods=["GET", "POST"], allow_headers=["Content-Type"],
    )
    register_error_handlers(app)
    app.include_router(health.router)
    for router in (garments.router, tryon.router, jobs.router, assets.router):
        app.include_router(router, prefix="/api")
    return app


app = create_app()
