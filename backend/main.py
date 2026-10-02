# Original entrypoint retained for restoration before PR if needed:
# from fastapi import FastAPI
#
# app = FastAPI(
#     title="Virtual Try-On Platform API",
#     version="0.1.0"
# )
#
# @app.get("/health")
# def health_check():
#     return {"status": "healthy"}

from backend.garment3d.app import create_app

app = create_app()
app.title = "Virtual Try-On Platform API"
