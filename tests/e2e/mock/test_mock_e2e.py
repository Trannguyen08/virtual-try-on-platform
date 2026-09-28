from backend.schemas.common import SuccessResponse
from backend.schemas.job import JobSchema


def test_backend_mock_upload_to_download(client, png_bytes):
    """HTTP-only handoff expected by M5; this does not test a frontend viewer."""
    garment = client.get("/api/garments").json()["data"][0]
    bodies = []
    jobs = []
    for height, size in [(165, "S"), (180, "XL")]:
        analyzed = client.post("/api/tryon/analyze", data={"height_cm": str(height)},
                               files={"image": ("demo.png", png_bytes, "image/png")})
        assert analyzed.status_code == 200
        body = analyzed.json()["data"]
        bodies.append(body)
        created = client.post("/api/tryon/fit", json={
            "body_id": body["body_id"], "garment_id": garment["garment_id"], "size": size,
        })
        assert created.status_code == 202
        response = client.get("/api/jobs/" + created.json()["data"]["job_id"])
        assert response.status_code == 200
        job = SuccessResponse[JobSchema].model_validate(response.json()).data
        jobs.append(job)
        assert job.result.body_id == body["body_id"] and job.result.size == size
        for asset in [body["mesh"], garment["mesh"], *job.result.assets.model_dump().values()]:
            assert asset["source"] == "mock"
            download = client.get(asset["url"])
            assert download.status_code == 200 and download.content.startswith(b"glTF")
    assert bodies[0]["body_id"] != bodies[1]["body_id"]
    assert jobs[0].job_id != jobs[1].job_id
    assert bodies[0]["measurements"]["chest_cm"] == bodies[1]["measurements"]["chest_cm"] == 96
