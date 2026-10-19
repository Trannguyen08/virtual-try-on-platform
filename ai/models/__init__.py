"""AI Models package for Module M4."""

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
