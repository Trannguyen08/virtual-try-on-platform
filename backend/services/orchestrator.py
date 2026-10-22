import warnings
from io import BytesIO
from typing import Protocol

from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

from backend.core.config import Settings
from backend.core.errors import AppException
from backend.db.repository import JobRepository
from backend.schemas.body import BodySchema
from backend.schemas.common import Source
from backend.schemas.fit import FitRequest, FitResultSchema
from backend.schemas.garment import GarmentSchema
from backend.services.job_manager import JobManager
from backend.services.storage import StorageService


class TryOnProvider(Protocol):
    """Adapters can compose real M1/M2/M4 implementations behind these methods."""

    source: Source

    def garments(self) -> list[GarmentSchema]: ...
    def analyze(self, image: bytes, height_cm: float) -> BodySchema: ...
    def fit(self, body: BodySchema, garment: GarmentSchema, request: FitRequest) -> FitResultSchema: ...


class TryOnOrchestrator:
    def __init__(self, settings: Settings, provider: TryOnProvider,
                 storage: StorageService, jobs: JobRepository):
        self.settings = settings
        self.provider = provider
        self.storage = storage
        self.jobs = JobManager(jobs)

    async def analyze(self, image: UploadFile, height_cm: float) -> BodySchema:
        try:
            content = await image.read(self.settings.max_image_bytes + 1)
        finally:
            await image.close()
        if len(content) > self.settings.max_image_bytes:
            raise AppException(413, "IMAGE_TOO_LARGE", "Image must be at most 5 MiB")
        formats = {"image/png": "PNG", "image/jpeg": "JPEG"}
        if image.content_type not in formats:
            raise AppException(415, "UNSUPPORTED_IMAGE_TYPE", "Only image/png and image/jpeg are accepted")
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(BytesIO(content)) as decoded:
                    if decoded.format != formats[image.content_type]:
                        raise ValueError("Declared media type does not match image")
                    if decoded.width * decoded.height > self.settings.max_image_pixels:
                        raise AppException(413, "IMAGE_TOO_LARGE", "Image must be at most 16 million pixels")
                    decoded.verify()
                # verify() alone does not fully decode JPEG data.
                with Image.open(BytesIO(content)) as decoded:
                    decoded.load()
        except (Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
            raise AppException(413, "IMAGE_TOO_LARGE", "Image pixel limit exceeded") from exc
        except (UnidentifiedImageError, OSError, ValueError, SyntaxError) as exc:
            raise AppException(400, "INVALID_IMAGE", "Image is empty, corrupt, or mismatches its media type") from exc
        body = self.provider.analyze(content, height_cm)
        self.storage.save_mock_body(body)
        return body

    def fit_inputs(self, request: FitRequest) -> tuple[BodySchema, GarmentSchema]:
        body = self.storage.get_mock_body(request.body_id)
        if body is None:
            raise AppException(404, "BODY_NOT_FOUND", "Body not found; submit analyze again")
        garment = next((g for g in self.provider.garments() if g.garment_id == request.garment_id), None)
        if garment is None:
            raise AppException(404, "GARMENT_NOT_FOUND", "Garment not found")
        if request.size not in {entry.size for entry in garment.sizes}:
            raise AppException(422, "SIZE_NOT_AVAILABLE", "Size is not available for this garment")
        return body, garment
