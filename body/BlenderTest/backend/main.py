"""
FastAPI Backend - Blender MPFB Web Integration
Quản lý job queue và giao tiếp với Blender headless
"""

import asyncio
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

import aiofiles
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# ─── Cấu hình đường dẫn ────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output"
SCRIPTS_DIR = BASE_DIR / "blender_scripts"
FRONTEND_DIR = BASE_DIR / "frontend"
OUTPUT_DIR.mkdir(exist_ok=True)

# ─── Đường dẫn Blender (chỉnh theo máy bạn) ────────────────────────────────
# Windows: thường là C:/Program Files/Blender Foundation/Blender X.X/blender.exe
BLENDER_PATH = os.environ.get(
    "BLENDER_PATH",
    r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
)

# ─── Job Store (in-memory, có thể upgrade lên Redis/DB) ────────────────────
jobs: Dict[str, Dict[str, Any]] = {}

# ─── Pydantic Models ────────────────────────────────────────────────────────

class ProportionsModel(BaseModel):
    shoulder_width: float = Field(0.5, ge=0.0, le=1.0)
    waist: float = Field(0.5, ge=0.0, le=1.0)
    hips: float = Field(0.5, ge=0.0, le=1.0)
    chest: float = Field(0.5, ge=0.0, le=1.0)
    leg_length: float = Field(0.5, ge=0.0, le=1.0)
    arm_length: float = Field(0.5, ge=0.0, le=1.0)
    muscle_tone: float = Field(0.3, ge=0.0, le=1.0)
    belly: float = Field(0.2, ge=0.0, le=1.0)
    buttocks: float = Field(0.5, ge=0.0, le=1.0)

class SkinModel(BaseModel):
    tone: str = Field("medium", description="light/medium/dark")
    color_hex: str = Field("#C68642")

class BodyParamsModel(BaseModel):
    height: float = Field(1.70, ge=1.4, le=2.1, description="Chiều cao (m)")
    weight: float = Field(65.0, ge=35.0, le=150.0, description="Cân nặng (kg)")
    age: int = Field(25, ge=10, le=80)
    gender: str = Field("female", description="male/female")
    proportions: ProportionsModel = ProportionsModel()
    skin: SkinModel = SkinModel()

class ClothingParamsModel(BaseModel):
    model_id: str
    clothing_id: str
    color_hex: Optional[str] = "#FFFFFF"
    size_override: Optional[float] = None  # 0.0-1.0, None = auto-fit

# ─── FastAPI App ────────────────────────────────────────────────────────────
app = FastAPI(
    title="Blender MPFB Web API",
    description="API tích hợp Blender MPFB với web interface",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static files
if FRONTEND_DIR.exists():
    app.mount("/app", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

# Serve output GLB files
app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")


# ─── Helper: Chạy Blender subprocess ────────────────────────────────────────

async def run_blender_script(script_name: str, params: dict, job_id: str) -> bool:
    """
    Chạy Blender headless với script Python.
    Returns True nếu thành công, False nếu lỗi.
    """
    script_path = SCRIPTS_DIR / script_name
    params_json = json.dumps(params)
    output_path = OUTPUT_DIR / f"{job_id}.glb"

    cmd = [
        BLENDER_PATH,
        "--background",           # Headless mode (không mở GUI)
        "--python", str(script_path),
        "--",                     # Separator: args sau đây là cho Python script
        "--job-id", job_id,
        "--output", str(output_path),
        "--params", params_json,
    ]

    jobs[job_id]["status"] = "processing"
    jobs[job_id]["command"] = " ".join(cmd)

    try:
        def run_subprocess():
            return subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

        process = await asyncio.to_thread(run_subprocess)
        stdout, stderr = process.stdout, process.stderr

        jobs[job_id]["blender_stdout"] = stdout.decode("utf-8", errors="replace") if stdout else ""
        jobs[job_id]["blender_stderr"] = stderr.decode("utf-8", errors="replace") if stderr else ""

        if process.returncode == 0 and output_path.exists():
            jobs[job_id]["status"] = "done"
            jobs[job_id]["glb_path"] = str(output_path)
            jobs[job_id]["glb_url"] = f"/output/{job_id}.glb"
            return True
        else:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = f"Blender exit code: {process.returncode}"
            return False

    except FileNotFoundError:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = (
            f"Không tìm thấy Blender tại: {BLENDER_PATH}\n"
            "Hãy set biến môi trường BLENDER_PATH hoặc chỉnh trong main.py"
        )
        return False
    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)
        return False


# ─── API Routes ─────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"message": "Blender MPFB Web API", "docs": "/docs", "app": "/app"}


@app.post("/api/generate")
async def generate_body(params: BodyParamsModel, background_tasks: BackgroundTasks):
    """
    Tạo 3D body model từ parameters.
    Trả về job_id để track tiến trình.
    """
    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {
        "id": job_id,
        "type": "generate_body",
        "status": "queued",
        "params": params.model_dump(),
        "created_at": asyncio.get_event_loop().time(),
    }

    # Chạy Blender trong background
    background_tasks.add_task(
        run_blender_script,
        "generate_body.py",
        params.model_dump(),
        job_id
    )

    return {
        "job_id": job_id,
        "status": "queued",
        "poll_url": f"/api/status/{job_id}",
        "message": "Đang xử lý, dùng poll_url để kiểm tra tiến trình"
    }


@app.post("/api/clothing")
async def apply_clothing(params: ClothingParamsModel, background_tasks: BackgroundTasks):
    """Apply clothing lên model đã tạo."""
    # Kiểm tra model_id tồn tại
    source_glb = OUTPUT_DIR / f"{params.model_id}.glb"
    if not source_glb.exists():
        raise HTTPException(status_code=404, detail=f"Model {params.model_id} không tồn tại")

    job_id = str(uuid.uuid4())[:8]
    clothing_params = params.model_dump()
    clothing_params["source_glb"] = str(source_glb)

    jobs[job_id] = {
        "id": job_id,
        "type": "apply_clothing",
        "status": "queued",
        "params": clothing_params,
    }

    background_tasks.add_task(
        run_blender_script,
        "apply_clothing.py",
        clothing_params,
        job_id
    )

    return {"job_id": job_id, "status": "queued", "poll_url": f"/api/status/{job_id}"}


@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """Kiểm tra trạng thái job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job không tồn tại")

    job = jobs[job_id]
    response = {
        "id": job["id"],
        "status": job["status"],  # queued | processing | done | error
        "type": job.get("type"),
    }

    if job["status"] == "done":
        response["glb_url"] = job.get("glb_url")
    elif job["status"] == "error":
        response["error"] = job.get("error")

    return response


@app.get("/api/models/{job_id}")
async def get_model_info(job_id: str):
    """Lấy thông tin đầy đủ về model đã tạo."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Model không tồn tại")
    return jobs[job_id]


@app.get("/api/clothing/list")
async def list_clothing():
    """Trả về danh sách clothing assets có sẵn."""
    # TODO: Đọc từ thư mục assets/clothing
    return {
        "items": [
            {"id": "tshirt_basic", "name": "T-Shirt Cơ Bản", "category": "tops", "preview": "/assets/clothing/tshirt_basic.png"},
            {"id": "jeans_straight", "name": "Quần Jeans Thẳng", "category": "bottoms", "preview": "/assets/clothing/jeans_straight.png"},
            {"id": "dress_summer", "name": "Váy Mùa Hè", "category": "dresses", "preview": "/assets/clothing/dress_summer.png"},
        ]
    }


@app.get("/api/jobs")
async def list_jobs():
    """Debug: Xem tất cả jobs."""
    return {"jobs": list(jobs.values()), "total": len(jobs)}


@app.delete("/api/jobs/clear")
async def clear_jobs():
    """Xoá tất cả jobs (dev only)."""
    jobs.clear()
    return {"message": "Cleared"}


# ─── Entry Point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    print("[START] Server dang chay tai: http://localhost:8000")
    print("[INFO]  API Docs: http://localhost:8000/docs")
    print("[INFO]  Web App:  http://localhost:8000/app")
    print(f"[INFO]  Blender path: {BLENDER_PATH}")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
