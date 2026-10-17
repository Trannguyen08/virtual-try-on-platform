import os
import sys
import io
import time
from pathlib import Path

# ============================================================
# 1. ÉP TOÀN BỘ TEMP & CACHE SANG Ổ D: (TRƯỚC KHI IMPORT THƯ VIỆN)
# ============================================================

PROJECT_ROOT = Path(
    r"D:\Năm 4 - Kỳ 1\Project\virtual-tryon\virtual-try-on-platform"
)

TMP_DIR = PROJECT_ROOT / "tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)
PARQUET_TMP_DIR = TMP_DIR / "hf_parquets"
PARQUET_TMP_DIR.mkdir(parents=True, exist_ok=True)

# Ghi đè toàn bộ biến môi trường tạm của Windows và Hugging Face
os.environ["TEMP"] = str(TMP_DIR)
os.environ["TMP"] = str(TMP_DIR)
os.environ["TMPDIR"] = str(TMP_DIR)
os.environ["HF_HOME"] = str(TMP_DIR / "hf_cache")
os.environ["HF_HUB_CACHE"] = str(TMP_DIR / "hf_cache" / "hub")
os.environ["HF_DATASETS_CACHE"] = str(TMP_DIR / "hf_cache" / "datasets")
os.environ["HUGGINGFACE_HUB_CACHE"] = str(TMP_DIR / "hf_cache" / "hub")

HF_TOKEN = os.getenv("HF_TOKEN", "")
if HF_TOKEN:
    os.environ["HF_TOKEN"] = HF_TOKEN
    os.environ["HUGGING_FACE_HUB_TOKEN"] = HF_TOKEN

# ============================================================
# 2. IMPORT CÁC THƯ VIỆN SAU KHI ĐÃ CẤU HÌNH PATH
# ============================================================

import pandas as pd
from PIL import Image
from huggingface_hub import HfApi, hf_hub_download

# ============================================================
# 3. ĐƯỜNG DẪN ĐẦU RA CHO DATASET
# ============================================================

OUTPUT_DIR = PROJECT_ROOT / "ai" / "dataset" / "data" / "fit_30k"
IMAGE_DIR = OUTPUT_DIR / "images"
CLOTH_DIR = IMAGE_DIR / "cloth"
PERSON_DIR = IMAGE_DIR / "person"
TARGET_DIR = IMAGE_DIR / "target"

CLOTH_DIR.mkdir(parents=True, exist_ok=True)
PERSON_DIR.mkdir(parents=True, exist_ok=True)
TARGET_DIR.mkdir(parents=True, exist_ok=True)

METADATA_PATH = OUTPUT_DIR / "metadata.csv"
DATASET_ID = "Yuanhao-Harry-Wang/fitvto-100k"
TARGET_NUM_SAMPLES = 30_000

# ============================================================
# 4. HELPER CHUYỂN ĐỔI ẢNH AN TOÀN
# ============================================================

def to_pil_rgb(data) -> Image.Image:
    """Chuyển đổi dữ liệu ảnh từ parquet sang PIL Image RGB."""
    if isinstance(data, Image.Image):
        return data.convert("RGB")
    if isinstance(data, dict) and "bytes" in data and data["bytes"]:
        return Image.open(io.BytesIO(data["bytes"])).convert("RGB")
    if isinstance(data, (bytes, bytearray)):
        return Image.open(io.BytesIO(data)).convert("RGB")
    raise ValueError(f"Không thể đọc kiểu ảnh: {type(data)}")

# ============================================================
# 5. KIỂM TRA TIẾN ĐỘ ĐÃ TẢI TRƯỚC ĐÓ (RESUME CAPABILITY)
# ============================================================

metadata_rows = []
downloaded_ids = set()

if METADATA_PATH.exists():
    try:
        existing_df = pd.read_csv(METADATA_PATH)
        metadata_rows = existing_df.to_dict("records")
        downloaded_ids = set(existing_df["id"].tolist())
        print(f"[*] Tìm thấy metadata cũ: Đã có sẵn {len(metadata_rows):,} samples.")
    except Exception as e:
        print(f"[!] Không đọc được metadata cũ ({e}), sẽ bắt đầu mới.")

# ============================================================
# 6. LẤY DANH SÁCH FILE PARQUET TỪ HUGGING FACE
# ============================================================

print("=" * 60)
print("Kết nối Hugging Face lấy danh sách Parquet...")
print("=" * 60)

api = HfApi(token=HF_TOKEN)
all_files = api.list_repo_files(repo_id=DATASET_ID, repo_type="dataset")
parquet_files = sorted(
    [f for f in all_files if f.startswith("data/train-") and f.endswith(".parquet")]
)

print(f"Tổng số file parquet trên repo: {len(parquet_files)} files.")
print(f"Mục tiêu tải: {TARGET_NUM_SAMPLES:,} mẫu.")
print(f"Toàn bộ dữ liệu tạm và ảnh lưu tại ổ D:")
print(f" - Temp Parquet : {PARQUET_TMP_DIR}")
print(f" - Output Images: {IMAGE_DIR}")
print("=" * 60)

# ============================================================
# 7. TẢI TUẦN TỰ TỪNG PARQUET -> TRÍCH XUẤT -> XÓA PARQUET TẠM
# ============================================================

current_count = len(metadata_rows)
start_time = time.time()

for p_idx, parquet_name in enumerate(parquet_files, start=1):
    if current_count >= TARGET_NUM_SAMPLES:
        break

    print(f"\n[Parquet {p_idx}/{len(parquet_files)}] Đang tải: {parquet_name}...")
    try:
        local_parquet_path = hf_hub_download(
            repo_id=DATASET_ID,
            filename=parquet_name,
            repo_type="dataset",
            token=HF_TOKEN,
            local_dir=PARQUET_TMP_DIR,
        )
    except Exception as e:
        print(f"[!] Lỗi tải file {parquet_name}: {e}. Đang thử file tiếp theo...")
        continue

    # Đọc file parquet cục bộ từ ổ D
    try:
        df = pd.read_parquet(local_parquet_path)
    except Exception as e:
        print(f"[!] Lỗi đọc parquet {local_parquet_path}: {e}")
        if os.path.exists(local_parquet_path):
            try:
                os.remove(local_parquet_path)
            except Exception:
                pass
        continue

    # Duyệt từng dòng trong parquet
    for _, row in df.iterrows():
        if current_count >= TARGET_NUM_SAMPLES:
            break

        current_count += 1
        sample_id = f"fit_{current_count:06d}"

        if sample_id in downloaded_ids:
            continue

        cloth_filename = f"{sample_id}.jpg"
        person_filename = f"{sample_id}.jpg"
        target_filename = f"{sample_id}.jpg"

        cloth_path = CLOTH_DIR / cloth_filename
        person_path = PERSON_DIR / person_filename
        target_path = TARGET_DIR / target_filename

        try:
            cloth_img = to_pil_rgb(row["cloth"])
            person_img = to_pil_rgb(row["person"])
            target_img = to_pil_rgb(row["target"])

            cloth_img.save(cloth_path, quality=95)
            person_img.save(person_path, quality=95)
            target_img.save(target_path, quality=95)

            metadata_rows.append(
                {
                    "id": sample_id,
                    "cloth_path": f"images/cloth/{cloth_filename}",
                    "person_path": f"images/person/{person_filename}",
                    "target_path": f"images/target/{target_filename}",
                    "body_bust": row.get("body_bust"),
                    "body_height": row.get("body_height"),
                    "body_hips": row.get("body_hips"),
                    "body_waist": row.get("body_waist"),
                    "garment_bust": row.get("garment_bust"),
                    "garment_length": row.get("garment_length"),
                    "garment_sleeve_length": row.get("garment_sleeve_length"),
                }
            )
            downloaded_ids.add(sample_id)
        except Exception as e:
            print(f"\n[Warning] Lỗi xử lý mẫu {sample_id}: {e}")
            continue

        if current_count % 100 == 0 or current_count == TARGET_NUM_SAMPLES:
            elapsed = time.time() - start_time
            speed = current_count / elapsed if elapsed > 0 else 0
            print(
                f"[{current_count:>5}/{TARGET_NUM_SAMPLES}] "
                f"{current_count / TARGET_NUM_SAMPLES * 100:6.2f}% | "
                f"Speed: {speed:.1f} samples/s"
            )

    # Lưu metadata định kỳ sau mỗi file parquet
    pd.DataFrame(metadata_rows).to_csv(METADATA_PATH, index=False, encoding="utf-8")

    # Xóa file parquet đã đọc xong để không chiếm dung lượng
    try:
        if os.path.exists(local_parquet_path):
            os.remove(local_parquet_path)
    except Exception:
        pass

# ============================================================
# 8. HOÀN TẤT & LƯU METADATA CUỐI CÙNG
# ============================================================

final_df = pd.DataFrame(metadata_rows)
final_df.to_csv(METADATA_PATH, index=False, encoding="utf-8")

print()
print("=" * 60)
print("DOWNLOAD COMPLETED THÀNH CÔNG 100%")
print("=" * 60)
print(f"Tổng mẫu tải được : {len(final_df):,}")
print(f"Metadata CSV     : {METADATA_PATH}")
print(f"Thư mục ảnh 3D   : {IMAGE_DIR}")
print("=" * 60)