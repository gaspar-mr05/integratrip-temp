from fastapi import FastAPI
from app.routers import auth, mcp
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

app = FastAPI()


app.include_router(auth.router)
app.include_router(mcp.router)


app.add_middleware(CORSMiddleware, allow_origins=[get_settings().FRONTEND_URL],
                    allow_credentials=True, 
                    allow_methods=["*"], 
                    allow_headers=["*"])

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/.well-known/oauth-client-metadata.json")
def oauth_client_metadata():
    settings = get_settings()
    metadata_url = f"{settings.BACKEND_URL}/.well-known/oauth-client-metadata.json"
    return {
        "client_id": metadata_url,
        "client_name": "IntegraTrip",
        "redirect_uris": [
            "https://integratrip-temp.onrender.com/mcp/cielo-sur/callback",
            "http://localhost:8000/mcp/cielo-sur/callback",
        ],
        "grant_types": ["authorization_code"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "none",
    }


