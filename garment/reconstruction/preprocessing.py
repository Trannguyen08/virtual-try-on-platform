from __future__ import annotations

import hashlib
import os
from collections.abc import Mapping
from pathlib import Path

from PIL import Image, ImageOps, ImageStat, UnidentifiedImageError

from .contracts import VIEW_ORDER, GarmentImage, GarmentView
from .errors import InvalidImageError

FORMAT_TO_MEDIA_TYPE = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
}


class ImagePreprocessor:
    def __init__(
        self,
        *,
        max_file_bytes: int = 10 * 1024 * 1024,
        target_dimension: int = 1024,
        low_resolution_threshold: int = 512,
        max_pixels: int = 100_000_000,
    ) -> None:
        self.max_file_bytes = max_file_bytes
        self.target_dimension = target_dimension
        self.low_resolution_threshold = low_resolution_threshold
        Image.MAX_IMAGE_PIXELS = max_pixels

    def process(
        self,
        sources: Mapping[GarmentView, Path],
        output_dir: Path,
    ) -> tuple[GarmentImage, ...]:
        if GarmentView.FRONT not in sources:
            raise InvalidImageError("FRONT_VIEW_REQUIRED", "Front image is required")
        if not 1 <= len(sources) <= 4:
            raise InvalidImageError(
                "INVALID_VIEW_COUNT", "Provide between one and four views"
            )

        output_dir.mkdir(parents=True, exist_ok=True)
        results: list[GarmentImage] = []
        checksums: set[str] = set()

        for view in VIEW_ORDER:
            source = sources.get(view)
            if source is None:
                continue
            result = self._process_one(view, source, output_dir)
            if result.sha256 in checksums:
                raise InvalidImageError(
                    "DUPLICATE_VIEW_IMAGE",
                    "The same image cannot be used for more than one view",
                )
            checksums.add(result.sha256)
            results.append(result)
        return tuple(results)

    def _process_one(
        self, view: GarmentView, source: Path, output_dir: Path
    ) -> GarmentImage:
        size = source.stat().st_size
        if size <= 0:
            raise InvalidImageError("EMPTY_IMAGE", f"{view.value} image is empty")
        if size > self.max_file_bytes:
            raise InvalidImageError(
                "IMAGE_TOO_LARGE", f"{view.value} image exceeds 10 MB"
            )

        try:
            with Image.open(source) as opened:
                detected_format = opened.format
                opened.verify()
            if detected_format not in FORMAT_TO_MEDIA_TYPE:
                raise InvalidImageError(
                    "UNSUPPORTED_IMAGE_FORMAT",
                    f"{view.value} must be JPEG, PNG, or WebP",
                )
            with Image.open(source) as opened:
                image = ImageOps.exif_transpose(opened)
                width, height = image.size
                warnings = list(self._quality_warnings(image, view))
                if min(width, height) < self.low_resolution_threshold:
                    warnings.append(f"{view.value.upper()}_LOW_RESOLUTION_UPSCALED")
                normalized = self._normalize_to_square(image)
                destination = output_dir / f"{view.value}.png"
                temporary = destination.with_suffix(".tmp")
                normalized.save(temporary, format="PNG", optimize=True)
                os.replace(temporary, destination)
        except InvalidImageError:
            raise
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise InvalidImageError(
                "INVALID_IMAGE",
                f"{view.value} image cannot be decoded",
            ) from exc

        digest = hashlib.sha256(destination.read_bytes()).hexdigest()
        return GarmentImage(
            view=view,
            path=destination,
            sha256=digest,
            media_type=FORMAT_TO_MEDIA_TYPE[detected_format],
            width=normalized.width,
            height=normalized.height,
            warnings=tuple(warnings),
        )

    def _normalize_to_square(self, image: Image.Image) -> Image.Image:
        has_alpha = "A" in image.getbands() or "transparency" in image.info
        mode = "RGBA" if has_alpha else "RGB"
        converted = image.convert(mode)
        contained = ImageOps.contain(
            converted,
            (self.target_dimension, self.target_dimension),
            method=Image.Resampling.LANCZOS,
        )
        background = (0, 0, 0, 0) if has_alpha else (255, 255, 255)
        canvas = Image.new(
            mode,
            (self.target_dimension, self.target_dimension),
            background,
        )
        offset = (
            (self.target_dimension - contained.width) // 2,
            (self.target_dimension - contained.height) // 2,
        )
        if has_alpha:
            canvas.paste(contained, offset, contained)
        else:
            canvas.paste(contained, offset)
        return canvas

    @staticmethod
    def _quality_warnings(image: Image.Image, view: GarmentView) -> tuple[str, ...]:
        grayscale = image.convert("L").resize((128, 128))
        mean = ImageStat.Stat(grayscale).mean[0]
        warnings: list[str] = []
        if mean < 25:
            warnings.append(f"{view.value.upper()}_IMAGE_VERY_DARK")
        elif mean > 240:
            warnings.append(f"{view.value.upper()}_IMAGE_OVEREXPOSED")
        return tuple(warnings)
