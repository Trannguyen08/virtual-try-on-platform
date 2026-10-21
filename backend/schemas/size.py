from backend.schemas.common import Confidence, Provenance, Size


class SizeRecommendationSchema(Provenance):
    size: Size | None
    confidence: Confidence
