"""Public garment API with dependencies loaded only when their exports are used.

Blender can import the standard-library-only MPFB catalog without importing
the separate NumPy/Trimesh mesh and simulation implementations.
"""

from importlib import import_module

__all__ = [
    "GarmentLoader",
    "GarmentChart",
    "SizeMeasurement",
    "SizeChartError",
    "GarmentMeshGenerator",
    "PantsMeshGenerator",
    "SizeScaler",
    "SizeScalingError",
    "ClothSimulator",
    "GeometricClothDraper",
    "DrapingError",
]

_EXPORT_MODULES = {
    **dict.fromkeys(
        ("GarmentLoader", "GarmentChart", "SizeMeasurement", "SizeChartError"),
        "garment.size_chart",
    ),
    **dict.fromkeys(
        ("GarmentMeshGenerator", "PantsMeshGenerator", "SizeScaler", "SizeScalingError"),
        "garment.mesh",
    ),
    **dict.fromkeys(
        ("ClothSimulator", "GeometricClothDraper", "DrapingError"),
        "garment.simulation",
    ),
}


def __getattr__(name):
    module_name = _EXPORT_MODULES.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(__all__))
