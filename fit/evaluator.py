"""Bộ đánh giá độ vừa vặn hình học 3D hoàn chỉnh (GeometryFitEvaluator).

Đóng gói trọn vẹn toàn bộ pipeline tính toán:
1. Penetration Metrics (FIT-01)
2. Distance Metrics (FIT-02)
3. Coverage Metrics (FIT-03)
4. Region Segmentation & Fit Status (FIT-04)
5. Fit Score & Classification (FIT-05)
6. Heatmap Payload Generation (FIT-06)
"""

from typing import Any, Dict, Optional
import trimesh

from shared.interfaces.fit import FitEvaluator
from fit.metrics.penetration import compute_penetration
from fit.metrics.distance import compute_distance
from fit.metrics.coverage import compute_coverage
from fit.region.region_fit import evaluate_region_fit
from fit.score.fit_score import evaluate_fit_score_breakdown
from fit.score.classification import classify_overall_fit
from fit.heatmap.heatmap_generator import generate_heatmap_payload
from fit.diagnostics import (
    generate_fit_diagnostics,
    generate_specs_comparison,
    generate_ai_fit_insights,
)


class GeometryFitEvaluator(FitEvaluator):
    """Lớp thực thi chính thức của interface FitEvaluator cho đánh giá hình học 3D kết hợp AI."""

    def __init__(self, garment_id: str = "tshirt_default", size: str = "M"):
        self.garment_id = garment_id
        self.size = size

    def evaluate(
        self,
        body_mesh: trimesh.Trimesh,
        garment_mesh: trimesh.Trimesh,
        target_torso_indices: Optional[Any] = None,
        body_measurements: Optional[Dict[str, float]] = None,
        garment_specs: Optional[Dict[str, float]] = None,
        custom_size_chart: Optional[Dict[str, Dict[str, float]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Thực hiện đánh giá toàn diện độ vừa vặn giữa Mesh người và Mesh áo.

        Args:
            body_mesh: Trimesh cơ thể (mét).
            garment_mesh: Trimesh áo (mét).
            target_torso_indices: Chỉ số đỉnh vùng torso để đo coverage (tùy chọn).

        Returns:
            Dictionary tổng hợp theo đúng hợp đồng dữ liệu chuẩn của hệ thống.
        """
        # 1. Tính toán 3 chỉ số cơ bản
        pen_res = compute_penetration(body_mesh, garment_mesh)
        dist_res = compute_distance(body_mesh, garment_mesh)
        cov_res = compute_coverage(body_mesh, garment_mesh, target_indices=target_torso_indices)

        # 2. Đánh giá độ vừa từng vùng
        region_res = evaluate_region_fit(
            body_mesh=body_mesh,
            garment_mesh=garment_mesh,
            per_vertex_distance=dist_res["per_vertex_distance"],
            is_penetrating=pen_res.get("is_penetrating"),
        )

        # 3. Tính điểm Fit Score tổng thể
        score_res = evaluate_fit_score_breakdown(pen_res, dist_res, cov_res)
        fit_score = score_res["fit_score"]

        # 4. Phân loại độ vừa tổng thể
        classification = classify_overall_fit(
            fit_score=fit_score,
            region_results=region_res,
            penetration_ratio=pen_res["penetration_ratio"],
        )

        # 5. Sinh dữ liệu Heatmap
        heatmap_payload = generate_heatmap_payload(
            per_vertex_distance_m=dist_res["per_vertex_distance"],
            is_penetrating=pen_res.get("is_penetrating"),
            garment_id=self.garment_id,
            size=self.size,
        )

        # 6. Chẩn đoán chi tiết vị trí chật / rộng / vừa
        diagnostics = generate_fit_diagnostics(
            region_results=region_res,
            penetration_results=pen_res,
            distance_results=dist_res,
        )

        # 7. Bảng đối chiếu thông số số đo cơ thể vs thông số áo (Specs Comparison)
        specs_comparison = generate_specs_comparison(
            body_measurements=body_measurements,
            current_size=self.size,
            custom_size_chart=custom_size_chart,
        )

        # 8. Tích hợp phân tích mô hình AI (SizeRecommender & FitPredictor)
        ai_insights = generate_ai_fit_insights(
            body_measurements=body_measurements,
            garment_specs=garment_specs,
            current_size=self.size,
            geometry_classification=classification,
            geometry_score=fit_score,
        )

        return {
            "fit_score": fit_score,
            "classification": classification,
            "metrics": {
                "penetration_ratio": pen_res["penetration_ratio"],
                "penetration_score": pen_res["penetration_score"],
                "max_penetration_depth_m": pen_res.get("max_penetration_depth", 0.0),
                "max_penetration_depth_cm": round(pen_res.get("max_penetration_depth", 0.0) * 100.0, 2),
                "avg_distance_m": dist_res["avg_distance"],
                "avg_distance_cm": round(dist_res["avg_distance"] * 100.0, 2),
                "distance_score": dist_res["distance_score"],
                "coverage_ratio": cov_res["coverage_ratio"],
                "coverage_score": cov_res["coverage_score"],
            },
            "regions": region_res,
            "diagnostics": diagnostics,
            "specs_comparison": specs_comparison,
            "ai_insights": ai_insights,
            "score_breakdown": score_res,
            "heatmap": heatmap_payload,
        }
