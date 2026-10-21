from typing import Literal

from backend.schemas.common import Confidence, Provenance, Score

FitLabel = Literal["tight", "good", "loose", "unknown"]


class PredictorSchema(Provenance):
    score: Score
    label: FitLabel
    confidence: Confidence
