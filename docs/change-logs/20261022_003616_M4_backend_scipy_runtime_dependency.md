# Declare SciPy for backend AI/fit imports

## Role and goal

M4 dependency integration. Fix backend startup failure caused by the AI router importing `fit.utils.proximity`, which requires SciPy.

## Files changed

- `backend/requirements.txt`: before, the backend install set included NumPy and Trimesh through its nested garment requirements but did not declare SciPy. After, `scipy>=1.12.0` is an explicit backend dependency.
- `requirements.txt` and `pyproject.toml`: already declared `scipy>=1.12.0`; unchanged.
- `backend/requirements-dev.txt`: already includes `backend/requirements.txt`; unchanged.

## Impact

The supported local backend install path (`pip install -r backend/requirements-dev.txt`) now installs the dependency used by `fit/utils/proximity.py`. No endpoint, schema, units, database, asset, or model behavior changed. M3 startup is affected because it imports the M4 router; M4 proximity calculations use SciPy's `cKDTree`.

## Root cause and resolution

`backend.main` imports `backend.api.ai`, which imports `ai.api.router`, then the Fit Score and penetration modules. `fit.utils.proximity` imports `scipy.spatial.cKDTree` at module load. Root project manifests already listed SciPy, but the documented backend-specific requirements path did not, leaving a fresh backend environment without it.

## Verification

Not run. The user provided a traceback showing `ModuleNotFoundError: No module named 'scipy'`. Pytest and backend startup were not run in this turn.

## Handoff

Install the updated development requirements in the existing environment, then restart Uvicorn. If import fails for another missing dependency, report the next traceback so the backend dependency set can be completed without installing the full AI/3D stack.
