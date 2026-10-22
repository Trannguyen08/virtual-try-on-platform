"""Định nghĩa hằng số phân vùng cơ thể và nhãn trạng thái độ vừa vặn từng vùng."""

from typing import List

# 4 Vùng cơ thể giải phẫu tiêu chuẩn
REGION_SHOULDER = "shoulder"
REGION_CHEST = "chest"
REGION_WAIST = "waist"
REGION_HIP = "hip"

ALL_REGIONS: List[str] = [
    REGION_SHOULDER,
    REGION_CHEST,
    REGION_WAIST,
    REGION_HIP,
]

# 3 Nhãn trạng thái độ vừa vặn từng vùng
STATUS_TIGHT = "TIGHT"  # Chật, bó sát
STATUS_GOOD = "GOOD"    # Vừa vặn, thoải mái
STATUS_LOOSE = "LOOSE"  # Rộng, thụng

FIT_STATUSES: List[str] = [
    STATUS_TIGHT,
    STATUS_GOOD,
    STATUS_LOOSE,
]

# Ngưỡng khoảng cách bề mặt từng vùng (Đơn vị: Mét)
# d < 0.5 cm -> TIGHT; 0.5 cm <= d <= 3.0 cm -> GOOD; d > 3.0 cm -> LOOSE
THRESHOLD_TIGHT_MAX_M = 0.005  # 0.5 cm
THRESHOLD_GOOD_MAX_M = 0.030   # 3.0 cm
