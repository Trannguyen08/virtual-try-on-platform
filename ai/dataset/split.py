"""Anti-Leakage Dataset Splitting Module for Module M4.

Performs group-based splitting (GroupShuffleSplit) using 'person_path' to ensure
that no person model appearing in the Test or Validation set was ever seen during Training.
"""

import sys
from pathlib import Path
from typing import Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

from ai.dataset.labeling.size_labeler import assign_size_labels, check_size_distribution

DEFAULT_DATA_DIR = PROJECT_ROOT / "ai" / "dataset" / "data" / "fit_30k"
DEFAULT_METADATA_PATH = DEFAULT_DATA_DIR / "metadata.csv"
DEFAULT_SPLIT_DIR = DEFAULT_DATA_DIR / "splits"


def split_dataset_by_person(
    df: pd.DataFrame,
    group_col: str = "person_path",
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Phân chia DataFrame thành 3 tập Train/Val/Test theo nhóm (person_path).

    Tuyệt đối không rò rỉ danh tính người mẫu (No Person Identity Leakage).

    Args:
        df: DataFrame chứa metadata gốc.
        group_col: Tên cột nhóm định danh người (mặc định 'person_path').
        train_ratio: Tỷ lệ tập huấn luyện (mặc định 0.70).
        val_ratio: Tỷ lệ tập kiểm định (mặc định 0.15).
        test_ratio: Tỷ lệ tập kiểm thử độc lập (mặc định 0.15).
        random_state: Seed tái lập kết quả (mặc định 42).

    Returns:
        Tuple (train_df, val_df, test_df).
    """
    total_ratio = train_ratio + val_ratio + test_ratio
    if not np.isclose(total_ratio, 1.0, atol=1e-5):
        raise ValueError(f"Tổng tỷ lệ chia phải bằng 1.0 (Hiện tại: {total_ratio})")

    if group_col not in df.columns:
        raise KeyError(f"Không tìm thấy cột nhóm '{group_col}' trong DataFrame.")

    # Bước 1: Tách Train (70%) và Temp (Val + Test = 30%)
    temp_ratio = val_ratio + test_ratio
    gss_1 = GroupShuffleSplit(
        n_splits=1,
        train_size=train_ratio,
        random_state=random_state,
    )
    train_idx, temp_idx = next(gss_1.split(df, groups=df[group_col]))

    train_df = df.iloc[train_idx].copy().reset_index(drop=True)
    temp_df = df.iloc[temp_idx].copy().reset_index(drop=True)

    # Bước 2: Tách Temp thành Val (50% của Temp) và Test (50% của Temp)
    val_relative_ratio = val_ratio / temp_ratio
    gss_2 = GroupShuffleSplit(
        n_splits=1,
        train_size=val_relative_ratio,
        random_state=random_state,
    )
    val_idx, test_idx = next(gss_2.split(temp_df, groups=temp_df[group_col]))

    val_df = temp_df.iloc[val_idx].copy().reset_index(drop=True)
    test_df = temp_df.iloc[test_idx].copy().reset_index(drop=True)

    # Bước 3: Kiểm tra toàn vẹn ranh giới (Zero Leakage Assertion)
    train_persons = set(train_df[group_col])
    val_persons = set(val_df[group_col])
    test_persons = set(test_df[group_col])

    overlap_train_val = train_persons & val_persons
    overlap_train_test = train_persons & test_persons
    overlap_val_test = val_persons & test_persons

    if overlap_train_val or overlap_train_test or overlap_val_test:
        raise AssertionError(
            f"Phát hiện rò rỉ danh tính người giữa các tập! "
            f"Train-Val: {len(overlap_train_val)}, "
            f"Train-Test: {len(overlap_train_test)}, "
            f"Val-Test: {len(overlap_val_test)}"
        )

    return train_df, val_df, test_df


def save_splits(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Lưu 3 tập Train/Val/Test thành file CSV riêng biệt.

    Args:
        train_df: DataFrame tập Train.
        val_df: DataFrame tập Val.
        test_df: DataFrame tập Test.
        output_dir: Thư mục lưu trữ.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(output_dir / "train.csv", index=False, encoding="utf-8")
    val_df.to_csv(output_dir / "val.csv", index=False, encoding="utf-8")
    test_df.to_csv(output_dir / "test.csv", index=False, encoding="utf-8")


def run_pipeline(
    metadata_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Chạy toàn bộ pipeline gán nhãn và chia tập chống leakage."""
    meta_p = metadata_path or DEFAULT_METADATA_PATH
    out_dir = output_dir or DEFAULT_SPLIT_DIR

    print("=" * 65)
    print("M4 DATASET SPLITTING PIPELINE (ANTI-LEAKAGE)")
    print("=" * 65)
    print(f"[*] Đọc dữ liệu từ : {meta_p}")

    df_raw = pd.read_csv(meta_p)
    print(f"[*] Số mẫu nạp vào : {len(df_raw):,} dòng")

    # 1. Gán nhãn Size Label
    print("\n[1/3] Gán nhãn kích cỡ Size Label...")
    df_labeled = assign_size_labels(df_raw)
    dist_report = check_size_distribution(df_labeled)
    print(f"[*] Phân phối kích cỡ: {dist_report['ratios']}")
    if not dist_report["is_valid"]:
        for w in dist_report["warnings"]:
            print(f"    [!] Cảnh báo: {w}")

    # 2. Chia tập GroupShuffleSplit
    print("\n[2/3] Chia tập Train (70%) / Val (15%) / Test (15%) theo person_path...")
    train_df, val_df, test_df = split_dataset_by_person(df_labeled)

    print(
        f"[*] Train set: {len(train_df):,} mẫu ({len(train_df)/len(df_labeled)*100:.1f}%) | "
        f"{train_df['person_path'].nunique():,} người"
    )
    print(
        f"[*] Val set  : {len(val_df):,} mẫu ({len(val_df)/len(df_labeled)*100:.1f}%) | "
        f"{val_df['person_path'].nunique():,} người"
    )
    print(
        f"[*] Test set : {len(test_df):,} mẫu ({len(test_df)/len(df_labeled)*100:.1f}%) | "
        f"{test_df['person_path'].nunique():,} người"
    )

    # 3. Lưu trữ kết quả
    print("\n[3/3] Xuất file CSV...")
    save_splits(train_df, val_df, test_df, out_dir)
    print(f"[OK] Đã lưu thành công tại: {out_dir}")
    print("=" * 65)

    return train_df, val_df, test_df


if __name__ == "__main__":
    run_pipeline()
