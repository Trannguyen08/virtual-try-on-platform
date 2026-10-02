from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx

from ..contracts import (
    GarmentView,
    GenerationRequest,
    ProviderResult,
    ProviderTask,
    ProviderTaskStatus,
    TaskState,
)
from ..errors import ProviderError


class TripoGarment3DProvider:
    name = "tripo"

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://openapi.tripo3d.ai/v3",
        model: str = "v3.1-20260211",
        client: httpx.AsyncClient | None = None,
        allowed_download_domains: tuple[str, ...] = ("tripo3d.ai",),
    ) -> None:
        if not api_key:
            raise ValueError(
                "TRIPO_API_KEY is required when the Tripo provider is enabled"
            )
        self.model = model
        self.allowed_download_domains = allowed_download_domains
        self._owns_client = client is None
        self.client = client or httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=httpx.Timeout(60.0, connect=10.0),
            follow_redirects=False,
        )

    async def create_task(self, request: GenerationRequest) -> ProviderTask:
        tokens: dict[GarmentView, str] = {}
        for image in request.images:
            tokens[image.view] = await self._upload(image.path)

        payload: dict[str, Any] = {
            "model": self.model,
            "texture": request.options.generate_texture,
            "pbr": request.options.generate_pbr,
            "texture_quality": "standard",
            "face_limit": request.options.target_face_count,
            "model_seed": request.options.seed,
            "texture_seed": request.options.seed,
            "enable_image_autofix": True,
        }
        if request.is_multi_view:
            payload.pop("enable_image_autofix", None)
            payload["inputs"] = [{view.value: tokens[view]} for view in tokens]
            endpoint = "/generation/multiview-to-model"
        else:
            payload["input"] = tokens[GarmentView.FRONT]
            payload["orientation"] = "align_image"
            endpoint = "/generation/image-to-model"

        data = await self._request_json("POST", endpoint, json=payload)
        task_id = data.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            raise ProviderError(
                "PROVIDER_INVALID_RESPONSE", "Tripo did not return a task ID"
            )
        return ProviderTask(provider=self.name, external_id=task_id)

    async def get_task(self, external_id: str) -> ProviderTaskStatus:
        data = await self._request_json("GET", f"/tasks/{external_id}")
        raw_state = data.get("status")
        state_map = {
            "queued": TaskState.QUEUED,
            "running": TaskState.RUNNING,
            "success": TaskState.SUCCESS,
            "failed": TaskState.FAILED,
            "cancelled": TaskState.CANCELLED,
        }
        try:
            state = state_map[raw_state]
        except KeyError as exc:
            raise ProviderError(
                "PROVIDER_INVALID_RESPONSE", "Tripo returned an unknown task state"
            ) from exc

        progress = data.get("progress", 0)
        progress = (
            max(0, min(100, int(progress))) if isinstance(progress, (int, float)) else 0
        )
        result = None
        if state is TaskState.SUCCESS:
            output = data.get("output") or {}
            model_url = output.get("model_url")
            if not isinstance(model_url, str):
                raise ProviderError(
                    "PROVIDER_INVALID_RESPONSE", "Completed Tripo task has no model URL"
                )
            result = ProviderResult(
                model_url=model_url,
                thumbnail_url=output.get("rendered_image_url"),
                metadata={"credits_consumed": data.get("credits_consumed")},
            )
        return ProviderTaskStatus(
            state=state,
            progress=progress,
            result=result,
            error_code=str(data.get("error_code"))
            if data.get("error_code") is not None
            else None,
            error_message=data.get("error_message"),
        )

    async def download(self, url: str, destination: Path, max_bytes: int) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix + ".part")
        total = 0
        try:
            current_url = url
            for redirect_count in range(4):
                self._validate_download_url(current_url)
                async with self.client.stream(
                    "GET",
                    current_url,
                    follow_redirects=False,
                    timeout=120.0,
                ) as response:
                    if response.is_redirect:
                        location = response.headers.get("location")
                        if not location:
                            raise ProviderError(
                                "PROVIDER_DOWNLOAD_FAILED",
                                "Provider returned an invalid redirect",
                            )
                        current_url = urljoin(current_url, location)
                        continue
                    response.raise_for_status()
                    with temporary.open("wb") as output:
                        async for chunk in response.aiter_bytes():
                            total += len(chunk)
                            if total > max_bytes:
                                raise ProviderError(
                                    "ARTIFACT_TOO_LARGE",
                                    "Provider artifact exceeds the size limit",
                                )
                            output.write(chunk)
                    break
            else:
                raise ProviderError(
                    "PROVIDER_DOWNLOAD_FAILED", "Provider returned too many redirects"
                )
            if total == 0:
                raise ProviderError(
                    "PROVIDER_DOWNLOAD_FAILED", "Provider returned an empty artifact"
                )
            os.replace(temporary, destination)
        except ProviderError:
            temporary.unlink(missing_ok=True)
            raise
        except (httpx.HTTPError, OSError) as exc:
            temporary.unlink(missing_ok=True)
            raise ProviderError(
                "PROVIDER_DOWNLOAD_FAILED",
                "Could not download the generated artifact",
                retryable=True,
            ) from exc

    async def cancel_task(self, external_id: str) -> bool:
        # Tripo cancellation is deliberately not assumed; local callers can stop polling.
        return False

    async def close(self) -> None:
        if self._owns_client:
            await self.client.aclose()

    async def _upload(self, path: Path) -> str:
        try:
            with path.open("rb") as stream:
                data = await self._request_json(
                    "POST",
                    "/files",
                    files={"file": (path.name, stream, "image/png")},
                )
        except OSError as exc:
            raise ProviderError(
                "INPUT_READ_FAILED", "Could not read a normalized input image"
            ) from exc
        token = data.get("file_token")
        if not isinstance(token, str) or not token:
            raise ProviderError(
                "PROVIDER_INVALID_RESPONSE", "Tripo did not return a file token"
            )
        return token

    async def _request_json(
        self, method: str, path: str, **kwargs: Any
    ) -> Mapping[str, Any]:
        try:
            response = await self.client.request(method, path, **kwargs)
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            raise ProviderError(
                "PROVIDER_UNAVAILABLE",
                "Tripo is temporarily unavailable",
                retryable=True,
                http_status=503,
            ) from exc

        # Tripo can return insufficient credits as HTTP 403. Interpret its
        # business error code before generic HTTP authentication errors.
        try:
            error_body = response.json()
        except ValueError:
            error_body = {}
        if isinstance(error_body, dict) and str(error_body.get("code")) == "2010":
            raise ProviderError(
                "PROVIDER_CREDITS_EXHAUSTED",
                "Tài khoản Tripo không đủ credit để tạo mô hình 3D. "
                "Hãy bổ sung credit trong Tripo API Platform rồi thử lại.",
                http_status=402,
            )
        if response.status_code == 429:
            raise ProviderError(
                "PROVIDER_RATE_LIMITED",
                "Tripo rate limit reached",
                retryable=True,
                http_status=503,
            )
        if response.status_code == 403:
            raise ProviderError(
                "PROVIDER_ACCESS_DENIED",
                "Tripo từ chối quyền thực hiện yêu cầu. Kiểm tra quyền API của tài khoản.",
                http_status=403,
            )
        if response.status_code == 401:
            raise ProviderError(
                "PROVIDER_AUTH_FAILED",
                "Tripo credentials were rejected",
                http_status=503,
            )
        if response.status_code >= 500:
            raise ProviderError(
                "PROVIDER_UNAVAILABLE",
                "Tripo is temporarily unavailable",
                retryable=True,
                http_status=503,
            )
        try:
            response.raise_for_status()
            body = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise ProviderError(
                "PROVIDER_INVALID_RESPONSE", "Tripo returned an invalid response"
            ) from exc
        if body.get("code") != 0:
            code = body.get("code")
            if code == 2010:
                raise ProviderError(
                    "PROVIDER_CREDITS_EXHAUSTED",
                    "Tripo credits are insufficient",
                    http_status=402,
                )
            raise ProviderError(
                "PROVIDER_REJECTED_REQUEST",
                str(body.get("message") or "Tripo rejected the request"),
                http_status=422,
            )
        data = body.get("data")
        if not isinstance(data, dict):
            raise ProviderError(
                "PROVIDER_INVALID_RESPONSE", "Tripo response has no data object"
            )
        return data

    def _validate_download_url(self, url: str) -> None:
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        if parsed.scheme != "https" or parsed.username or parsed.password:
            raise ProviderError(
                "UNSAFE_ARTIFACT_URL", "Provider artifact URL is not allowed"
            )
        if not any(
            hostname == domain or hostname.endswith(f".{domain}")
            for domain in self.allowed_download_domains
        ):
            raise ProviderError(
                "UNSAFE_ARTIFACT_URL", "Provider artifact host is not allowed"
            )
