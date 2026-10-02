from pathlib import Path

import pytest
from PIL import Image

from garment.reconstruction.contracts import GarmentView
from garment.reconstruction.errors import InvalidImageError
from garment.reconstruction.preprocessing import ImagePreprocessor


def image(path: Path, color=(80, 120, 200)) -> Path:
    Image.new("RGB", (512, 640), color).save(path, format="JPEG")
    return path


def test_preprocessor_orders_and_normalizes_views(tmp_path: Path) -> None:
    preprocessor = ImagePreprocessor()
    result = preprocessor.process(
        {
            GarmentView.BACK: image(tmp_path / "back.jpg", (20, 30, 40)),
            GarmentView.FRONT: image(tmp_path / "front.jpg"),
        },
        tmp_path / "normalized",
    )

    assert [item.view for item in result] == [GarmentView.FRONT, GarmentView.BACK]
    assert all(item.path.suffix == ".png" and item.path.is_file() for item in result)
    assert result[0].width == 1024
    assert result[0].height == 1024


def test_preprocessor_requires_front_view(tmp_path: Path) -> None:
    with pytest.raises(InvalidImageError, match="Front image") as error:
        ImagePreprocessor().process(
            {GarmentView.BACK: image(tmp_path / "back.jpg")},
            tmp_path / "normalized",
        )
    assert error.value.code == "FRONT_VIEW_REQUIRED"


def test_preprocessor_rejects_duplicate_images(tmp_path: Path) -> None:
    source = image(tmp_path / "same.jpg")
    with pytest.raises(InvalidImageError) as error:
        ImagePreprocessor().process(
            {GarmentView.FRONT: source, GarmentView.BACK: source},
            tmp_path / "normalized",
        )
    assert error.value.code == "DUPLICATE_VIEW_IMAGE"


def test_preprocessor_upscales_small_image_instead_of_rejecting_it(
    tmp_path: Path,
) -> None:
    source = tmp_path / "small.png"
    Image.new("RGB", (120, 240), (100, 120, 140)).save(source, format="PNG")

    result = ImagePreprocessor().process(
        {GarmentView.FRONT: source},
        tmp_path / "normalized",
    )[0]

    assert (result.width, result.height) == (1024, 1024)
    assert "FRONT_LOW_RESOLUTION_UPSCALED" in result.warnings
    with Image.open(result.path) as normalized:
        assert normalized.size == (1024, 1024)
        assert normalized.getpixel((0, 0)) == (255, 255, 255)
