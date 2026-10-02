from pathlib import Path
from types import SimpleNamespace

from garment.reconstruction.postprocessing import (
    BlenderPostProcessor,
    PassthroughPostProcessor,
)


def test_passthrough_copies_source(tmp_path: Path) -> None:
    source = tmp_path / "source.glb"
    destination = tmp_path / "model.glb"
    source.write_bytes(b"mesh")

    PassthroughPostProcessor().process(source, destination, 30_000)

    assert destination.read_bytes() == b"mesh"


def test_blender_processor_builds_headless_command(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "source.glb"
    destination = tmp_path / "model.glb"
    script = tmp_path / "process.py"
    source.write_bytes(b"source")
    script.write_text("# fixture", encoding="utf-8")
    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        destination.write_bytes(b"processed")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("subprocess.run", fake_run)
    BlenderPostProcessor(executable="blender", script=script).process(
        source, destination, 30_000
    )

    assert captured["command"][:3] == ["blender", "--background", "--factory-startup"]
    assert captured["command"][-1] == "30000"
    assert destination.read_bytes() == b"processed"
