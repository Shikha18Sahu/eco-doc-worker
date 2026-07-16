from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.workflow_routes import router as workflow_router
from app.db.database import init_db

app = FastAPI(title="Autonomous AI Document Processing Worker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "eko-doc-worker-backend"}


app.include_router(workflow_router, prefix="/api")