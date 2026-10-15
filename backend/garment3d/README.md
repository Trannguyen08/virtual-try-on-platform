# Local garment image-to-3D service

This service converts one to four garment photographs into an input-derived,
textured GLB and a `garment-fit-ready/1.0` metadata document. The default
provider runs locally and does not upload user images to a third party.

## What the local pipeline produces

- A segmented garment preview with transparency.
- A real triangle mesh containing curved front/back panels and seam geometry.
- Front texture from the uploaded image; a supplied back view is used for the
  back texture, otherwise the front is mirrored and a warning is returned.
- Category-specific 2D landmarks and their nearest GLB vertex indices.
- Garment measurements, confidence, provenance, attachment regions, and
  opening vertex groups for body integration.
- A GLB in right-handed, Y-up, +Z-forward coordinates using metres.
- API measurements in centimetres.

This is a parametric reconstruction. It does not claim to recover invisible
geometry from a single image. `fit_ready` is only true when the request includes
a real garment measurement for pixel-to-centimetre calibration.

## Install and run on Windows

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install -r backend\garment3d\requirements-dev.txt
.venv\Scripts\python -m uvicorn backend.garment3d.app:app --port 8000
```

Set `GARMENT3D_PROVIDER=local` in the repository `.env` file before starting.
The service intentionally treats that ignored file as its configuration source.

Open `http://localhost:8000/docs` for the API explorer.

## API flow

Create a reconstruction with `POST /garment3d/generations`. Form fields:

- `front`: required JPEG, PNG, WebP, or BMP garment image.
- `left`, `back`, `right`: optional additional views.
- `garment_type`: `tshirt`, `shirt`, `jacket`, `pants`, `skirt`, or `dress`.
- `reference_measurement`: use `garment_length` for the current UI flow.
- `reference_value_cm`: the real value of that measurement in centimetres.

Poll `GET /garment3d/jobs/{job_id}`, then read the generation response. Completed
responses provide download URLs for GLB, transparent preview, and metadata JSON.

## Segmentation input guidance

Best results come from a flat garment, a contrasting plain background, even
lighting, no body or hanger occluding the contour, and the full item inside the
frame. A transparent PNG is preferred. If a safe mask cannot be obtained, the
pipeline fails with `GARMENT_MASK_NOT_DETECTED` rather than returning a fake
model.

## Providers

- `local` (default): self-hosted OpenCV/NumPy/Trimesh pipeline.
- `mock`: deterministic triangle fixture for CI and API plumbing tests only.
- `tripo`: legacy optional cloud adapter. It is not the default and sends input
  outside the self-hosted system when explicitly enabled.

## Licenses

- OpenCV 4.5+: Apache-2.0.
- Trimesh: MIT.
- NumPy: BSD-3-Clause.
- Pillow: HPND.

No AI checkpoint is required by the default local pipeline. Model weights and
datasets must remain outside Git.

## Optional Blender post-processing

```powershell
$env:GARMENT3D_POSTPROCESSOR = "blender"
$env:BLENDER_EXECUTABLE = "C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"
```

The default `passthrough` mode avoids requiring Blender and preserves landmark
vertex indices. Blender may reorder topology, so the service marks such output
as `fit_ready=false` until bindings are regenerated.
