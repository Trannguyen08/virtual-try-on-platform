"""Interface định nghĩa hợp đồng của bộ đánh giá độ vừa vặn hình học 3D (FitEvaluator)."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class FitEvaluator(ABC):
    """Interface trừu tượng cho việc đánh giá độ vừa vặn giữa Mesh cơ thể và Mesh quần áo."""

    @abstractmethod
    def evaluate(self, body_mesh: Any, garment_mesh: Any, **kwargs: Any) -> Dict[str, Any]:
        """Tính toán các chỉ số hình học, phân lớp từng vùng và điểm Fit tổng thể.

        Args:
            body_mesh: Đối tượng trimesh.Trimesh đại diện cho cơ thể người 3D (đơn vị: mét).
            garment_mesh: Đối tượng trimesh.Trimesh đại diện cho trang phục 3D (đơn vị: mét).

        Returns:
            Dictionary chứa kết quả đánh giá theo đúng hợp đồng dữ liệu.
        """
        pass
