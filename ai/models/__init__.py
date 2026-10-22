"""AI Models package for Module M4."""

try:
    from ai.models.size_recommender import (
        FEATURE_COLUMNS,
        DummySizeRecommender,
        MLSizeRecommender,
        RuleBasedSizeRecommender,
        SizeRecommender,
    )
    from ai.models.fit_predictor import (
        FIT_FEATURE_COLUMNS,
        DummyFitPredictor,
        FitPredictor,
        MLFitPredictor,
        RuleBasedFitPredictor,
    )
except ImportError:
    FEATURE_COLUMNS = []
    FIT_FEATURE_COLUMNS = []
    RuleBasedSizeRecommender = None
    DummySizeRecommender = None
    MLSizeRecommender = None
    SizeRecommender = None
    RuleBasedFitPredictor = None
    DummyFitPredictor = None
    MLFitPredictor = None
    FitPredictor = None
from ai.models.dynamic_size_advisor import (
    AnthropometricEstimator,
    GarmentDimensionPredictor,
    DynamicSizeMatcher,
    DynamicSizeAdvisor,
)

__all__ = [
    "FEATURE_COLUMNS",
    "RuleBasedSizeRecommender",
    "DummySizeRecommender",
    "MLSizeRecommender",
    "SizeRecommender",
    "FIT_FEATURE_COLUMNS",
    "RuleBasedFitPredictor",
    "DummyFitPredictor",
    "MLFitPredictor",
    "FitPredictor",
    "AnthropometricEstimator",
    "GarmentDimensionPredictor",
    "DynamicSizeMatcher",
    "DynamicSizeAdvisor",
]
