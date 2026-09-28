from fastapi import Request

from backend.services.orchestrator import TryOnOrchestrator


def get_orchestrator(request: Request) -> TryOnOrchestrator:
    return request.app.state.orchestrator
