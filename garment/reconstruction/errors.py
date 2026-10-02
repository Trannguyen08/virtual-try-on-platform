from __future__ import annotations


class ReconstructionError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        retryable: bool = False,
        http_status: int = 422,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable
        self.http_status = http_status


class InvalidImageError(ReconstructionError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(code, message, http_status=422)


class ProviderError(ReconstructionError):
    def __init__(
        self,
        code: str,
        message: str,
        *,
        retryable: bool = False,
        http_status: int = 502,
    ) -> None:
        super().__init__(code, message, retryable=retryable, http_status=http_status)


class InvalidMeshError(ReconstructionError):
    def __init__(self, message: str) -> None:
        super().__init__("INVALID_MESH", message, http_status=502)
