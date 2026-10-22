"""Typed replacement seam for future M1/M2/M4 adapters; no AI imports."""

import json
from pathlib import Path
from uuid import uuid4

from backend.schemas.body import BodyMeasurementSchema, BodySchema
from backend.schemas.fit import FitRequest, FitResultSchema, RegionFitSchema
from backend.schemas.garment import GarmentSchema
from backend.schemas.predictor import PredictorSchema
from backend.schemas.simulation import SimulationSchema
from backend.schemas.size import SizeRecommendationSchema
from backend.services.assets import mock_asset


class MockProvider:
    source = "mock"

    def __init__(self, asset_dir: Path):
        self.asset_dir = asset_dir

    def garments(self) -> list[GarmentSchema]:
        fixture = Path(__file__).resolve().parents[1] / "fixtures" / "catalog.json"
        return [GarmentSchema(
            **json.loads(fixture.read_text(encoding="utf-8")),
            mesh=mock_asset(self.asset_dir, "mock-tshirt.glb"),
        )]

    def analyze(self, image: bytes, height_cm: float) -> BodySchema:
        # Image is validated by the orchestrator but deliberately not used to measure.
        return BodySchema(
            body_id=f"body_{uuid4().hex}", source="mock", method="fixed_demo_measurements",
            notes=["height_cm is user supplied; other measurements are fixed synthetic fixtures.",
                   "No person detection, image-based measurement, or AI inference is performed."],
            measurements=BodyMeasurementSchema(
                height_cm=height_cm, chest_cm=96, waist_cm=80, hip_cm=98, shoulder_width_cm=44,
            ),
            confidence=None, mesh=mock_asset(self.asset_dir, "mock-body.glb"),
        )

    def fit(self, body: BodySchema, garment: GarmentSchema, request: FitRequest) -> FitResultSchema:
        # Deliberately illustrative labels, not scores calculated from body or garment.
        label = {"S": "tight", "M": "good", "L": "loose", "XL": "loose"}[request.size]
        provenance = {
            "source": "mock", "method": "fixed_demo_fit",
            "notes": ["Labels are scripted by size for UI testing; not an actual fit evaluation."],
        }
        return FitResultSchema(
            **provenance, body_id=body.body_id, garment_id=garment.garment_id, size=request.size,
            recommendation=SizeRecommendationSchema(
                source="mock", method="fixed_demo_recommendation", size="M", confidence=None,
                notes=["Always M for the demo; not a personalized recommendation."],
            ),
            overall=PredictorSchema(**provenance, score=None, label=label, confidence=None),
            regions=[RegionFitSchema(**provenance, region=region, score=None,
                                     label=label, confidence=None)
                     for region in ("chest", "waist", "hip", "shoulder")],
            assets=SimulationSchema(
                body_mesh=body.mesh, garment_mesh=garment.mesh,
                tryon_mesh=mock_asset(self.asset_dir, "mock-tryon.glb"),
            ),
        )
