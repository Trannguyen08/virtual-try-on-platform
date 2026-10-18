"""Module Fit: Tính toán Hình học 3D, Đánh giá Độ vừa Vặn và Heatmap cho Virtual Try-On."""

from fit.metrics.penetration import compute_penetration
from fit.metrics.distance import compute_distance
from fit.metrics.coverage import compute_coverage
from fit.region.body_regions import segment_body_regions
from fit.region.region_fit import evaluate_region_fit
from fit.score.fit_score import compute_fit_score, evaluate_fit_score_breakdown
from fit.score.classification import classify_overall_fit
from fit.heatmap.heatmap_generator import generate_heatmap_payload
from fit.heatmap.heatmap_exporter import export_heatmap_json, validate_heatmap_schema
from fit.evaluator import GeometryFitEvaluator

__all__ = [
    "compute_penetration",
    "compute_distance",
    "compute_coverage",
    "segment_body_regions",
    "evaluate_region_fit",
    "compute_fit_score",
    "evaluate_fit_score_breakdown",
    "classify_overall_fit",
    "generate_heatmap_payload",
    "export_heatmap_json",
    "validate_heatmap_schema",
    "GeometryFitEvaluator",
]
