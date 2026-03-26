import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes.analyze import router as analyze_router
from backend.api.routes.chat import router as chat_router
from backend.api.models.schemas import HealthResponse  # Ensure backend/api/models/schemas.py exists with HealthResponse class

app = FastAPI(
    title="NeighborIQ API",
    description="AI-powered hyperlocal real estate intelligence",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)
app.include_router(chat_router)


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", version="1.0.0")


@app.get("/")
async def root():
    return {"message": "NeighborIQ API", "docs": "/docs"}