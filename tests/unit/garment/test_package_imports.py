"""Regression coverage for catalog imports in Blender's lean Python runtime."""

from pathlib import Path
import subprocess
import sys
import textwrap


def test_blender_catalog_without_mesh_dependencies_tc_gar_06():
    """Test Case ID: TC-GAR-06.

    Target: Import the Blender clothing catalog/alignment without Trimesh.
    Expected: No mesh/simulation import; lightweight public exports still work.
    """
    script = textwrap.dedent("""
        import importlib.abc
        import sys

        class BlockMeshDependencies(importlib.abc.MetaPathFinder):
            def find_spec(self, fullname, path=None, target=None):
                if fullname.split('.')[0] in {'trimesh', 'numpy', 'scipy'}:
                    raise ModuleNotFoundError('Dependency intentionally blocked: ' + fullname)
                return None

        sys.meta_path.insert(0, BlockMeshDependencies())
        import garment
        from garment.mpfb.catalog import load_catalog
        from garment.external.alignment import reference_scale
        from garment import GarmentLoader
        from garment.size_chart import GarmentLoader as OriginalLoader

        assert callable(load_catalog)
        assert callable(reference_scale)
        assert GarmentLoader is OriginalLoader
        assert garment.GarmentLoader is OriginalLoader
        assert 'GarmentMeshGenerator' in dir(garment)
        assert 'garment.mesh' not in sys.modules
        assert 'garment.simulation' not in sys.modules
        assert 'trimesh' not in sys.modules
        try:
            garment.unknown_export
        except AttributeError:
            pass
        else:
            raise AssertionError('Unknown exports must raise AttributeError')
    """)
    result = subprocess.run(
        [sys.executable, "-S", "-c", script],
        cwd=Path(__file__).resolve().parents[3],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
