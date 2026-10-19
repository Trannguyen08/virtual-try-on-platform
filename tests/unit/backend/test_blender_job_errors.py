"""Regression checks for Blender failures hidden behind exit code zero."""

import logging
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from backend.services import blender_body


@pytest.mark.parametrize("exit_code", [0, 1])
def test_script_failure_keeps_job_failed_and_logs_reason_tc_api_03(
    tmp_path, caplog, exit_code,
):
    """Test Case ID: TC-API-03.

    Target: Blender Python exception with no exported clothing asset.
    Expected: Failed job even on exit 0; useful diagnostic in server log;
    generic client error; Python exception exit flag supplied to Blender.
    """
    jobs = blender_body.BlenderBodyJobs()
    job = jobs.create("clothing", {})
    result = SimpleNamespace(returncode=exit_code, stdout="Blender quit",
                             stderr="ValueError: Cannot sample a continuous torso for T-shirt")
    with (
        patch.object(blender_body, "OUTPUT", tmp_path),
        patch.object(blender_body, "find_blender_executable", return_value="blender"),
        patch.object(blender_body.subprocess, "run", return_value=result) as process,
        caplog.at_level(logging.ERROR),
    ):
        jobs.run(job["job_id"], {})
    failed = jobs.get(job["job_id"])
    assert failed["status"] == "failed"
    assert failed["asset_url"] is None
    assert "Cannot sample a continuous torso" in caplog.text
    assert "ValueError" not in failed["error"]
    command = process.call_args.args[0]
    assert command[command.index("--python-exit-code") + 1] == "1"
