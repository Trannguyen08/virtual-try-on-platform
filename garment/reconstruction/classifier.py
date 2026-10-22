from __future__ import annotations

import cv2
import numpy as np


def auto_detect_garment_type(
    mask: np.ndarray, rgb: np.ndarray | None = None
) -> str:
    """Analyze garment silhouette geometry and texture to classify garment category.

    Categories:
    - 'pants': Lower half splits into two distinct leg columns.
    - 'dress': Elongated continuous vertical silhouette (tall & slender) without leg split.
    - 'skirt': Waistband at top without sleeves, flaring outward to hem.
    - 'shirt': Top garment with sleeve wings and central vertical placket/button seam.
    - 'tshirt': Default top garment with sleeve wings and continuous front fabric.
    """
    ys, xs = np.nonzero(mask)
    if not len(xs):
        return "tshirt"
    top, bottom = int(ys.min()), int(ys.max())
    left, right = int(xs.min()), int(xs.max())
    h = max(1, bottom - top + 1)
    w = max(1, right - left + 1)
    aspect_ratio = float(w) / float(h)

    def row_spans(fraction: float, min_gap: int = 6) -> tuple[int, int]:
        target_y = int(np.clip(round(top + fraction * h), 0, mask.shape[0] - 1))
        row = mask[target_y, left : right + 1]
        runs = []
        in_run = False
        start = 0
        for idx, val in enumerate(row):
            if val and not in_run:
                in_run = True
                start = idx
            elif not val and in_run:
                in_run = False
                runs.append((start, idx - 1))
        if in_run:
            runs.append((start, len(row) - 1))
        merged = []
        for r in runs:
            if not merged:
                merged.append(r)
            elif r[0] - merged[-1][1] <= min_gap:
                merged[-1] = (merged[-1][0], r[1])
            else:
                merged.append(r)
        valid = [r for r in merged if (r[1] - r[0] + 1) >= 4]
        tot_w = sum(r[1] - r[0] + 1 for r in valid)
        return len(valid), tot_w

    lower_fractions = [0.65, 0.72, 0.80, 0.86]
    two_leg_count = 0
    for f in lower_fractions:
        spans, _ = row_spans(f)
        if spans >= 2:
            two_leg_count += 1

    # 1. Pants: Lower half splits into 2 distinct leg columns
    if two_leg_count >= 2 and aspect_ratio < 0.85:
        return "pants"

    # 2. Dress: Very tall/long garment without leg split
    _, w_top = row_spans(0.12)
    _, w_chest = row_spans(0.30)
    _, w_waist = row_spans(0.50)
    _, w_hem = row_spans(0.90)

    if aspect_ratio < 0.68 and two_leg_count == 0:
        return "dress"

    # 3. Skirt: Starts at waist (no sleeves), wide bottom
    if aspect_ratio < 1.25 and w_hem > 1.25 * max(1, w_top) and w_chest <= 1.05 * max(1, w_waist):
        top_row_mask = mask[top : top + max(2, int(h * 0.08)), left : right + 1]
        if np.mean(top_row_mask) > 0.40:
            return "skirt"

    # 4. Shirt vs Tshirt: check for button placket down vertical center
    if rgb is not None:
        cx = (left + right) // 2
        y_start = int(top + 0.15 * h)
        y_end = int(top + 0.75 * h)
        if y_end > y_start + 20 and 0 <= cx < rgb.shape[1]:
            center_strip = rgb[y_start:y_end, max(0, cx - 4) : min(rgb.shape[1], cx + 5)]
            gray_strip = cv2.cvtColor(center_strip, cv2.COLOR_RGB2GRAY)
            dy = np.abs(np.diff(gray_strip.astype(np.float32), axis=0))
            button_transitions = np.sum(dy > 35.0)
            if button_transitions >= 18:
                return "shirt"

    return "tshirt"
