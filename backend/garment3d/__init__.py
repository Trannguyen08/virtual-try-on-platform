"""Isolated FastAPI vertical slice for garment image-to-3D generation.

The package deliberately has no eager app import so domain/repository users do not
need optional multipart dependencies merely to import a submodule.
"""
