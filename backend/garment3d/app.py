from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from garment.reconstruction.config import get_preset
from garment.reconstruction.postprocessing import (
    BlenderPostProcessor,
    PassthroughPostProcessor,
)
from garment.reconstruction.preprocessing import ImagePreprocessor
from garment.reconstruction.providers import (
    MockGarment3DProvider,
    TripoGarment3DProvider,
)
from garment.reconstruction.validation import GlbValidator

from .repository import JobRepository
from .router import router
from .service import Garment3DService
from .settings import Garment3DSettings


def create_app(settings: Garment3DSettings | None = None) -> FastAPI:
    active_settings = settings or Garment3DSettings.from_environment()
    active_settings.validate()
    get_preset(active_settings.preset)

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        active_settings.output_dir.mkdir(parents=True, exist_ok=True)
        repository = JobRepository(active_settings.sqlite_path)
        repository.initialize()
        if active_settings.provider == "tripo":
            provider = TripoGarment3DProvider(
                api_key=active_settings.tripo_api_key,
                base_url=active_settings.tripo_base_url,
                model=active_settings.tripo_model,
            )
        else:
            provider = MockGarment3DProvider(active_settings.output_dir / ".mock")

        if active_settings.postprocessor == "blender":
            postprocessor = BlenderPostProcessor(
                executable=active_settings.blender_executable,
                script=active_settings.blender_script,
            )
        else:
            postprocessor = PassthroughPostProcessor()

        application.state.garment3d_settings = active_settings
        application.state.garment3d_service = Garment3DService(
            repository=repository,
            provider=provider,
            preprocessor=ImagePreprocessor(
                max_file_bytes=active_settings.max_upload_bytes
            ),
            validator=GlbValidator(max_file_bytes=active_settings.max_artifact_bytes),
            postprocessor=postprocessor,
            output_dir=active_settings.output_dir,
            preset=active_settings.preset,
            max_artifact_bytes=active_settings.max_artifact_bytes,
            poll_cache_seconds=active_settings.poll_cache_seconds,
        )
        yield
        await provider.close()

    application = FastAPI(
        title="Garment Image-to-3D API",
        version="0.1.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(router)

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "healthy", "provider": active_settings.provider}

    return application


app = create_app()
