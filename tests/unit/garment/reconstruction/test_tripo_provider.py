import asyncio
import json
from pathlib import Path

import httpx
import pytest
from PIL import Image

from garment.reconstruction.config import get_preset
from garment.reconstruction.contracts import (
    GarmentImage,
    GarmentView,
    GenerationRequest,
    TaskState,
)
from garment.reconstruction.providers.tripo import TripoGarment3DProvider
from garment.reconstruction.errors import ProviderError


@pytest.mark.parametrize("status,code,expected", [
    (403, 2010, "PROVIDER_CREDITS_EXHAUSTED"),
    (402, 2010, "PROVIDER_CREDITS_EXHAUSTED"),
    (401, 1002, "PROVIDER_AUTH_FAILED"),
    (403, 1002, "PROVIDER_ACCESS_DENIED"),
])
def test_provider_distinguishes_credit_and_auth_errors(status, code, expected):
    async def scenario():
        async with httpx.AsyncClient(
            base_url="https://openapi.tripo3d.ai/v3",
            transport=httpx.MockTransport(lambda request: httpx.Response(
                status, json={"code": code, "message": "Provider rejected request"}
            )),
        ) as client:
            provider = TripoGarment3DProvider(api_key="test-key", client=client)
            with pytest.raises(ProviderError) as caught:
                await provider._request_json("POST", "/generation/multiview-to-model")
            assert caught.value.code == expected
            if code == 2010:
                assert caught.value.http_status == 402
    asyncio.run(scenario())


def garment_image(path: Path, view: GarmentView, value: int) -> GarmentImage:
    Image.new("RGB", (512, 512), (value, value, value)).save(path, format="PNG")
    return GarmentImage(view, path, str(value) * 64, "image/png", 512, 512)


def test_tripo_uses_multiview_endpoint_and_maps_success(tmp_path: Path) -> None:
    uploads = iter(["file_front", "file_back"])
    generation_payload = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/files"):
            return httpx.Response(
                200, json={"code": 0, "data": {"file_token": next(uploads)}}
            )
        if request.url.path.endswith("/generation/multiview-to-model"):
            generation_payload.update(json.loads(request.content))
            return httpx.Response(
                200, json={"code": 0, "data": {"task_id": "task_123"}}
            )
        if request.url.path.endswith("/tasks/task_123"):
            return httpx.Response(
                200,
                json={
                    "code": 0,
                    "data": {
                        "status": "success",
                        "progress": 100,
                        "output": {
                            "model_url": "https://cdn.tripo3d.ai/model.glb",
                            "rendered_image_url": "https://cdn.tripo3d.ai/preview.png",
                        },
                    },
                },
            )
        raise AssertionError(request.url)

    async def scenario() -> None:
        client = httpx.AsyncClient(
            base_url="https://openapi.tripo3d.ai/v3",
            transport=httpx.MockTransport(handler),
        )
        provider = TripoGarment3DProvider(api_key="secret", client=client)
        request = GenerationRequest(
            images=(
                garment_image(tmp_path / "front.png", GarmentView.FRONT, 10),
                garment_image(tmp_path / "back.png", GarmentView.BACK, 20),
            ),
            options=get_preset("balanced").to_options(),
        )
        task = await provider.create_task(request)
        status = await provider.get_task(task.external_id)
        await client.aclose()
        assert task.external_id == "task_123"
        assert status.state is TaskState.SUCCESS
        assert status.result and status.result.model_url.endswith("model.glb")

    asyncio.run(scenario())
    assert generation_payload["inputs"] == [
        {"front": "file_front"},
        {"back": "file_back"},
    ]
    assert generation_payload["face_limit"] == 30_000
    assert "enable_image_autofix" not in generation_payload
