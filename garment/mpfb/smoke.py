"""User-run real Blender acceptance matrix through the running local API.

Creates three synthetic bodies and fits the configured demo garments. This
checks exports/provenance; screenshots are still needed to judge appearance.
"""

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import struct
import sys
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .catalog import REPO


def request(api, path, payload=None):
    content = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = Request(api.rstrip("/") + path, data=content,
                  headers={"Content-Type": "application/json"} if content is not None else {})
    try:
        with urlopen(req, timeout=30) as response:
            envelope = json.load(response)
    except HTTPError as exc:
        try:
            message = json.load(exc).get("error", {}).get("message", "API request failed")
        except (ValueError, AttributeError):
            message = "API request failed"
        raise ValueError(f"HTTP {exc.code}: {message}") from exc
    if envelope.get("error") or envelope.get("data") is None:
        raise ValueError("API trả response lỗi hoặc không có data")
    return envelope["data"]


def wait_job(api, job, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        job = request(api, f"/api/body-builder/jobs/{job['job_id']}")
        if job["status"] == "completed":
            return job
        if job["status"] == "failed":
            raise ValueError(job.get("error") or "Blender job failed")
        time.sleep(2)
    raise ValueError("Hết thời gian chờ job Blender; kiểm tra log backend")


def body_parameters(weight, proportions):
    values = {name: 0.5 for name in (
        "shoulder_width", "waist", "hips", "chest", "leg_length",
        "arm_length", "muscle_tone", "belly", "buttocks",
    )}
    values.update(proportions)
    return {"height_cm": 170, "weight_kg": weight, "age": 25,
            "gender": "male", "skin_color": "#b8b8b8", "proportions": values}


def main():
    parser = argparse.ArgumentParser(description="Kiểm tra refit thật: 3 body × quần áo mẫu")
    parser.add_argument("--api", default="http://127.0.0.1:8000")
    parser.add_argument("--timeout", type=float, default=240)
    parser.add_argument("--output", type=Path, default=REPO / "data/outputs/mpfb-validation")
    parser.add_argument("--garments", nargs="+", default=["mpfb-tshirt", "mpfb-pants", "mpfb-outfit"])
    args = parser.parse_args()
    available = {g["id"]: g for g in request(args.api, "/api/body-builder/garments")}
    for identifier in args.garments:
        if identifier not in available or not available[identifier]["available"]:
            raise ValueError(f"{identifier}: thiếu asset; chạy bước cài/check trước")
    destination = args.output / datetime.now(timezone(timedelta(hours=7))).strftime("%Y%m%d_%H%M%S_%f")
    destination.mkdir(parents=True, exist_ok=False)
    report = {"mode": "real_api_export_validation", "visual_quality_verified": False, "runs": []}
    cases = {
        "lean": body_parameters(50, {"waist": 0.35, "chest": 0.4}),
        "average": body_parameters(65, {}),
        "full": body_parameters(95, {"waist": 0.75, "chest": 0.7, "hips": 0.7}),
    }
    report_path = destination / "report.json"
    for name, parameters in cases.items():
        row = {"body_case": name, "parameters": parameters, "status": "running", "garments": []}
        report["runs"].append(row)
        started = time.monotonic()
        try:
            body = wait_job(args.api, request(args.api, "/api/body-builder/generate", parameters), args.timeout)
            row["body_job_id"] = body["job_id"]
            for identifier in args.garments:
                entry = available[identifier]
                payload = {"body_job_id": body["job_id"], "garment_id": identifier,
                           "category": entry["category"], "size": "M", "color_hex": "#ffffff"}
                job = wait_job(args.api, request(args.api, "/api/body-builder/clothing", payload), args.timeout)
                if job["method"] != "blender_mpfb_refit" or job["source"] != "module":
                    raise ValueError("Kết quả không phải native MPFB refit")
                with urlopen(args.api.rstrip("/") + job["asset_url"], timeout=30) as response:
                    blob = response.read(64 * 1024 * 1024 + 1)
                if len(blob) < 12 or len(blob) > 64 * 1024 * 1024:
                    raise ValueError("GLB rỗng hoặc vượt giới hạn 64 MiB")
                magic, version, length = struct.unpack("<4sII", blob[:12])
                if magic != b"glTF" or version != 2 or length != len(blob):
                    raise ValueError("Header/độ dài GLB không hợp lệ")
                filename = f"{name}_{identifier}.glb"
                (destination / filename).write_bytes(blob)
                row["garments"].append({"garment_id": identifier, "job_id": job["job_id"],
                                        "method": job["method"], "file": filename,
                                        "bytes": len(blob), "status": "export_valid"})
                print(f"{name} / {identifier}: GLB hợp lệ; cần kiểm tra hình ảnh", flush=True)
            row["status"] = "export_valid"
        except (OSError, ValueError) as exc:
            row["status"] = "failed"
            row["error"] = str(exc)
        finally:
            row["seconds"] = round(time.monotonic() - started, 2)
            report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        if row["status"] == "failed":
            print(f"Kiểm tra dừng do lỗi; xem {report_path}", file=sys.stderr)
            return 1
    print(f"Báo cáo và GLB: {destination}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as exc:
        print(f"Kiểm tra MPFB thất bại: {exc}", file=sys.stderr)
        sys.exit(1)
