from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import auth, mcp, oauth_client_metadata

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_settings().FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(mcp.router)
app.include_router(oauth_client_metadata.router)


@app.get("/health")
def health():
    return {"status": "ok"}
