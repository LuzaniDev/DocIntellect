from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import documents, health
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Plataforma de RPA inteligente para processamento e extracao de dados de documentos com OCR + NLP",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])


@app.get("/")
async def root():
    return {"app": settings.app_name, "version": settings.app_version, "status": "running"}
