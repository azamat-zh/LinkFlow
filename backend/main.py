from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import matching, onboarding, relationships, workflows
from services import firebase_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    firebase_client.get_db()
    yield


app = FastAPI(title="LinkFlow API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(onboarding.router, prefix="/api")
app.include_router(matching.router, prefix="/api")
app.include_router(relationships.router, prefix="/api")
app.include_router(workflows.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
