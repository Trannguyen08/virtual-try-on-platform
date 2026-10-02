from __future__ import annotations

import os
from pathlib import Path

from fastapi import UploadFile

from garment.reconstruction.errors import InvalidImageError


async def save_upload(upload: UploadFile, destination: Path, max_bytes: int) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    total = 0
    try:
        with temporary.open("wb") as output:
            while chunk := await upload.read(1024 * 1024):
                total += len(chunk)
                if total > max_bytes:
                    raise InvalidImageError(
                        "IMAGE_TOO_LARGE", "Each image must be 10 MB or smaller"
                    )
                output.write(chunk)
        if total == 0:
            raise InvalidImageError("EMPTY_IMAGE", "Uploaded image is empty")
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
        await upload.close()
