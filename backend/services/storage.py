"""Validated asset registration and body persistence for the main API."""

import hashlib
import re
from pathlib import Path

from backend.core.config import Settings
from backend.core.errors import AppException
from backend.db.repository import AssetRepository, BodyRepository
from backend.schemas.body import BodySchema
from backend.services.assets import ASSET_NAMES

KINDS = frozenset({"original_image", "foreground_image", "mesh", "texture", "glb"})
PUBLIC_GLB_NAME = re.compile(r"^[a-zA-Z0-9_-]+\.glb$")


class StorageService:
    def __init__(self, settings: Settings, bodies: BodyRepository, assets: AssetRepository):
        self.settings = settings
        self.bodies = bodies
        self.assets = assets

    def save_mock_body(self, body: BodySchema) -> None:
        self.bodies.create_mock(body)

    def get_mock_body(self, body_id: str) -> BodySchema | None:
        record = self.bodies.get(body_id)
        if record is None or record.kind != "mock_analyzed" or record.status != "ready":
            return None
        return BodySchema.model_validate(record.schema_json)

    def register_asset(self, path: Path, *, kind: str, scope: str = "managed",
                       media_type: str, public_name: str | None = None,
                       body_id: str | None = None, job_id: str | None = None,
                       metadata: dict | None = None):
        if kind not in KINDS or scope not in {"managed", "fixture"}:
            raise ValueError("Invalid asset kind or storage scope")
        if public_name is not None and (kind != "glb" or not PUBLIC_GLB_NAME.fullmatch(public_name)):
            raise ValueError("Only GLB assets may have a safe public name")
        root = (self.settings.asset_dir if scope == "fixture" else self.settings.managed_asset_dir).resolve()
        resolved = path.resolve()
        if not resolved.is_relative_to(root) or not resolved.is_file():
            raise ValueError("Asset must be an existing file inside its storage root")
        if scope == "fixture" and public_name not in ASSET_NAMES:
            raise ValueError("Only allowlisted fixtures may be registered")
        digest = hashlib.sha256()
        with resolved.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
        return self.assets.create(
            kind=kind, scope=scope, key=resolved.relative_to(root).as_posix(),
            media_type=media_type, byte_size=resolved.stat().st_size,
            sha256=digest.hexdigest(), public_name=public_name,
            body_id=body_id, job_id=job_id, metadata=metadata,
        )

    def seed_fixtures(self) -> None:
        for name in ASSET_NAMES:
            path = self.settings.asset_dir / name
            existing = self.assets.get_by_public_name(name)
            if existing is not None:
                status = "available" if path.is_file() else "missing"
                if existing.status != status:
                    self.assets.update_status(existing.asset_id, status)
                continue
            if path.is_file():
                self.register_asset(path, kind="glb", scope="fixture",
                                    media_type="model/gltf-binary", public_name=name)

    def register_mpfb_body(self, body_id: str, mesh_path: Path, *, metadata: dict | None = None):
        """Register an existing managed MPFB GLB without exposing a filesystem path."""
        self.bodies.create_mpfb(body_id, metadata=metadata)
        try:
            asset = self.register_asset(
                mesh_path, kind="glb", media_type="model/gltf-binary",
                public_name=f"body-{body_id}.glb", body_id=body_id,
                metadata={"method": "blender_mpfb"},
            )
        except Exception:
            self.bodies.update_status(body_id, "failed", error_code="ASSET_REGISTRATION_FAILED")
            raise
        self.bodies.update_status(body_id, "ready")
        return asset

    def mpfb_body_path(self, body_id: str) -> Path:
        record = self.bodies.get(body_id)
        if record is None or record.kind != "mpfb" or record.status != "ready":
            raise AppException(404, "BODY_NOT_FOUND", "MPFB body was not found")
        name = f"body-{body_id}.glb"
        try:
            return self.asset_path(name)
        except AppException as exc:
            raise AppException(404, "BODY_ASSET_NOT_FOUND", "MPFB body asset is unavailable") from exc

    def asset_path(self, name: str) -> Path:
        if not PUBLIC_GLB_NAME.fullmatch(name):
            raise AppException(404, "ASSET_NOT_FOUND", "Asset not found")
        asset = self.assets.get_by_public_name(name)
        if asset is None or asset.kind != "glb" or asset.status != "available":
            raise AppException(404, "ASSET_NOT_FOUND", "Asset not found")
        root = (self.settings.asset_dir if asset.storage_scope == "fixture"
                else self.settings.managed_asset_dir).resolve()
        path = (root / asset.storage_key).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            if asset.status != "missing":
                self.assets.update_status(asset.asset_id, "missing")
            raise AppException(404, "ASSET_NOT_FOUND", "Asset not found")
        return path
