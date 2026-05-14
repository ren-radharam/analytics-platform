from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import api_keys, auth, dashboards, events

app = FastAPI(title="Analytics Platform API", version="1.0.0", docs_url="/docs")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-vercel-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(api_keys.router, prefix="/api/v1")
app.include_router(dashboards.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "analytics-platform"}
