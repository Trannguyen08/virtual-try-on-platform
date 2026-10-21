import logging
from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import assets, body_builder, garments, health, image_tryon, jobs, tryon
from backend.core.config import Settings
from backend.core.errors import register_error_handlers
from backend.db.repository import AssetRepository, BodyRepository, ImageTryOnRepository, JobRepository
from backend.db.session import make_engine, make_session_factory
from backend.garment3d.app import create_app as create_garment3d_app
from backend.garment3d.settings import Garment3DSettings
from backend.schemas.common import ErrorResponse
from backend.services.mock_provider import MockProvider
from backend.services.blender_body import BlenderBodyJobs
from backend.services.image_tryon import ImageTryOnService
from backend.services.orchestrator import TryOnOrchestrator, TryOnProvider
from backend.services.storage import StorageService


startup_logger = logging.getLogger("uvicorn.error")


def create_app(
    settings: Settings | None = None,
    provider: TryOnProvider | None = None,
    garment3d_settings: Garment3DSettings | None = None,
) -> FastAPI:
    settings = settings or Settings()
    engine = make_engine(settings.database_url)
    sessions = make_session_factory(engine)
    storage = StorageService(settings, BodyRepository(sessions), AssetRepository(sessions))
    jobs_repo = JobRepository(sessions)
    garment_app = create_garment3d_app(
        garment3d_settings, route_prefix="", use_cors=False
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        try:
            from backend.db.models import Base

            step_started = perf_counter()
            startup_logger.info("Startup: checking database schema")
            Base.metadata.create_all(engine)
            startup_logger.info("Startup: database schema ready in %.2fs", perf_counter() - step_started)

            step_started = perf_counter()
            startup_logger.info("Startup: registering fixture assets")
            storage.seed_fixtures()
            startup_logger.info("Startup: fixture assets ready in %.2fs", perf_counter() - step_started)

            step_started = perf_counter()
            startup_logger.info("Startup: initializing Garment 3D")
            async with garment_app.router.lifespan_context(garment_app):
                startup_logger.info("Startup: Garment 3D ready in %.2fs", perf_counter() - step_started)
                yield
        finally:
            engine.dispose()

    app = FastAPI(
        title="Virtual Try-On Platform API", version="0.1.0",
        description=(
            "Legacy fit routes use mock data. Image try-on reconstructs garment "
            "geometry locally and composes a static MPFB scene in Blender."
        ),
        responses={status: {"model": ErrorResponse} for status in (400, 404, 413, 415, 422, 500)},
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.storage = storage
    app.state.body_jobs = BlenderBodyJobs(storage)
    app.state.image_tryon = ImageTryOnService(
        settings, storage, ImageTryOnRepository(sessions),
    )
    app.state.orchestrator = TryOnOrchestrator(
        settings, provider or MockProvider(settings.asset_dir), storage, jobs_repo,
    )
    app.add_middleware(
        CORSMiddleware, allow_origins=list(settings.cors_origins), allow_credentials=False,
        allow_methods=["GET", "POST", "PUT"], allow_headers=["Content-Type"],
    )
    register_error_handlers(app)
    app.include_router(health.router)
    for router in (garments.router, tryon.router, image_tryon.router,
                   jobs.router, assets.router, body_builder.router):
        app.include_router(router, prefix="/api")
    app.mount("/garment3d", garment_app)
    return app


app = create_app()
