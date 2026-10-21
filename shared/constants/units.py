"""Định nghĩa hằng số đơn vị đo và chuyển đổi tiêu chuẩn trong toàn bộ dự án."""

# Đơn vị đo dài chuẩn
UNIT_INTERNAL = "m"  # Chuẩn nội bộ: Mét (m) cho tính toán hình học 3D
UNIT_EXTERNAL = "cm"  # Chuẩn ngoại vi: Centimet (cm) cho API và hiển thị người dùng

# Hệ số chuyển đổi
M_TO_CM = 100.0
CM_TO_M = 0.01


def to_cm(val_m: float) -> float:
    """Chuyển đổi từ Mét sang Centimet, làm tròn 1 chữ số thập phân (1 mm)."""
    return round(float(val_m) * M_TO_CM, 1)


def to_m(val_cm: float) -> float:
    """Chuyển đổi từ Centimet sang Mét."""
    return float(val_cm) * CM_TO_M
