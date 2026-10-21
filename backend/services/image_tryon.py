"""Accept calibrated garment photographs for the durable try-on worker."""

import hashlib
import os
import shutil
import warnings
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

from backend.core.config import Settings
from backend.core.errors import AppException
from backend.db.repository import ImageTryOnRepository
from backend.schemas.image_tryon import ImageTryOnJob, ImageTryOnRequest
from backend.services.storage import StorageService
from garment.reconstruction.errors import InvalidMeshError
from garment.reconstruction.validation import GlbValidator

MEDIA_FORMATS = {
    "image/jpeg": "JPEG", "image/png": "PNG", "image/webp": "WEBP",
}


class ImageTryOnService:
    def __init__(self, settings: Settings, storage: StorageService,
                 jobs: ImageTryOnRepository) -> None:
        self.settings = settings
        self.storage = storage
        self.jobs = jobs

    async def submit(self, request: ImageTryOnRequest,
                     uploads: dict[str, UploadFile | None]) -> ImageTryOnJob:
        body_path = self.storage.mpfb_body_path(request.body_id)
        body_record = self.storage.bodies.get(request.body_id)
        frame = body_record.metadata_json if body_record else {}
        if any(frame.get(key) != value for key, value in {
            "mesh_unit": "m", "up_axis": "Y", "forward_axis": "+Z",
        }.items()):
            raise AppException(422, "BODY_FRAME_INVALID", "MPFB body frame is not registered")
        try:
            GlbValidator(max_file_bytes=100 * 1024 * 1024).validate(body_path)
        except (InvalidMeshError, OSError) as exc:
            raise AppException(422, "BODY_ASSET_INVALID", "MPFB body GLB is invalid") from exc
        if uploads.get("front") is None:
            raise AppException(422, "FRONT_VIEW_REQUIRED", "Front garment image is required")
        validated: dict[str, tuple[bytes, str]] = {}
        for view, upload in uploads.items():
            if upload is not None:
                validated[view] = await self._read_image(upload)
        job_id = f"itry_{uuid4().hex}"
        root = self.settings.managed_asset_dir.resolve()
        input_dir = root / "image_tryon" / job_id / "inputs"
        images: list[dict] = []
        views: dict[str, str] = {}
        try:
            input_dir.mkdir(parents=True, exist_ok=False)
            for view, (content, media_type) in validated.items():
                path = input_dir / f"{view}.image"
                temporary = input_dir / f"{view}.part"
                temporary.write_bytes(content)
                os.replace(temporary, path)
                key = path.relative_to(root).as_posix()
                views[view] = key
                images.append({
                    "view": view, "key": key, "media_type": media_type,
                    "byte_size": len(content),
                    "sha256": hashlib.sha256(content).hexdigest(),
                })
            internal_request = request.model_dump(mode="json")
            internal_request["views"] = views
            return self.jobs.enqueue(job_id, request.body_id, internal_request, images)
        except Exception:
            shutil.rmtree(input_dir.parent, ignore_errors=True)
            raise

    def get(self, job_id: str) -> ImageTryOnJob:
        job = self.jobs.get(job_id)
        if job is None:
            raise AppException(404, "JOB_NOT_FOUND", "Try-on job was not found")
        return job

    async def _read_image(self, upload: UploadFile) -> tuple[bytes, str]:
        try:
            content = await upload.read(self.settings.max_garment_image_bytes + 1)
        finally:
            await upload.close()
        if len(content) > self.settings.max_garment_image_bytes:
            raise AppException(413, "IMAGE_TOO_LARGE", "Each garment image must be at most 10 MiB")
        if upload.content_type not in MEDIA_FORMATS:
            raise AppException(415, "UNSUPPORTED_IMAGE_TYPE", "Use JPEG, PNG or WebP garment images")
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(BytesIO(content)) as opened:
                    if opened.format != MEDIA_FORMATS[upload.content_type]:
                        raise ValueError("Image media type does not match its content")
                    if opened.width * opened.height > self.settings.max_garment_image_pixels:
                        raise AppException(413, "IMAGE_TOO_LARGE", "Image exceeds 16 million pixels")
                    opened.verify()
                with Image.open(BytesIO(content)) as opened:
                    opened.load()
        except (Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
            raise AppException(413, "IMAGE_TOO_LARGE", "Image pixel limit exceeded") from exc
        except (UnidentifiedImageError, OSError, ValueError, SyntaxError) as exc:
            raise AppException(400, "INVALID_IMAGE", "Garment image is empty or invalid") from exc
        return content, upload.content_type
