"""
Module: garment.simulation.simulator
Task ID: GAR-05, GAR-06
Test Case ID: TC-GAR-05, TC-GAR-06

Trình điều phối mô phỏng vải ClothSimulator.
Tự động tích hợp kép:
- Engine chính: Blender Headless Simulation (khi có Blender cài trên máy).
- Engine dự phòng: GeometricClothDraper (Zero-Crash Fallback siêu nhanh khi không có Blender).
- Đảm bảo xuất file draped.glb hợp lệ, exit code 0, xử lý timeout rõ ràng, không treo máy.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Union

import trimesh

from garment.simulation.draping import GeometricClothDraper, DrapingError

logger = logging.getLogger(__name__)


class ClothSimulator:
    """Bộ điều phối mô phỏng vải thông minh (Hybrid Cloth Simulator)."""

    BLENDER_SCRIPT_PATH = Path(__file__).parent / "blender" / "blender_cloth_sim.py"

    def __init__(
        self,
        blender_executable: Optional[str] = None,
        default_timeout_seconds: int = 180,
    ) -> None:
        self.blender_executable = blender_executable or shutil.which("blender")
        self.default_timeout_seconds = default_timeout_seconds
        self.geometric_draper = GeometricClothDraper()

    def is_blender_available(self) -> bool:
        """Kiểm tra máy có sẵn Blender CLI hay không."""
        return self.blender_executable is not None

    def simulate(
        self,
        body_input: Union[trimesh.Trimesh, Path, str],
        garment_input: Union[trimesh.Trimesh, Path, str],
        output_glb_path: Union[Path, str],
        prefer_engine: str = "auto",  # 'auto', 'blender', 'geometric'
        timeout_seconds: Optional[int] = None,
    ) -> Path:
        """
        Thực thi mô phỏng vải và xuất ra file draped.glb:
        - prefer_engine='blender': Buộc dùng Blender (lỗi nếu không có).
        - prefer_engine='geometric': Dùng thuật toán hình học nhanh thuần Python.
        - prefer_engine='auto': Ưu tiên Blender nếu có; tự động fallback về Geometric nếu không có hoặc lỗi.
        """
        output_path = Path(output_glb_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        timeout = timeout_seconds or self.default_timeout_seconds

        # Nạp Trimesh objects nếu cần
        body_mesh: trimesh.Trimesh
        if isinstance(body_input, trimesh.Trimesh):
            body_mesh = body_input
        else:
            body_mesh = trimesh.load(str(body_input), force="mesh")

        garment_mesh: trimesh.Trimesh
        if isinstance(garment_input, trimesh.Trimesh):
            garment_mesh = garment_input
        else:
            garment_mesh = trimesh.load(str(garment_input), force="mesh")

        use_blender = False
        if prefer_engine == "blender":
            if not self.is_blender_available():
                raise DrapingError("Không tìm thấy executable 'blender' trong PATH hệ thống.")
            use_blender = True
        elif prefer_engine == "auto":
            use_blender = self.is_blender_available()

        if use_blender:
            try:
                self._run_blender_cli(
                    body_mesh=body_mesh,
                    garment_mesh=garment_mesh,
                    output_path=output_path,
                    timeout=timeout,
                )
                if output_path.is_file() and output_path.stat().st_size > 0:
                    return output_path
            except Exception as exc:
                logger.warning(
                    f"Mô phỏng Blender gặp sự cố ({exc}). Tự động kích hoạt Geometric Fallback..."
                )

        # Fallback hoặc Chế độ Geometric Draping thuần Python
        draped_mesh = self.geometric_draper.drape(
            body_mesh=body_mesh,
            garment_mesh=garment_mesh,
        )

        output_path.write_bytes(draped_mesh.export(file_type="glb"))
        return output_path

    def _run_blender_cli(
        self,
        body_mesh: trimesh.Trimesh,
        garment_mesh: trimesh.Trimesh,
        output_path: Path,
        timeout: int,
    ) -> None:
        """Chạy Blender process ở chế độ headless CLI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_p = Path(tmpdir)
            body_file = tmp_p / "body_temp.obj"
            garment_file = tmp_p / "garment_temp.obj"

            body_file.write_bytes(body_mesh.export(file_type="obj").encode("utf-8"))
            garment_file.write_bytes(garment_mesh.export(file_type="obj").encode("utf-8"))

            cmd = [
                self.blender_executable,
                "--background",
                "--factory-startup",
                "--python",
                str(self.BLENDER_SCRIPT_PATH),
                "--",
                "--body",
                str(body_file),
                "--garment",
                str(garment_file),
                "--output",
                str(output_path),
                "--frames",
                "40",
            ]

            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
            )

            if process.returncode != 0:
                raise DrapingError(f"Blender exit code {process.returncode}: {process.stderr}")
