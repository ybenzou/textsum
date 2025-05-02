from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import routes

app = FastAPI(
    title="Summarizer API",
    description="Summarize text using local BART + optional LoRA models.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(routes.router)
