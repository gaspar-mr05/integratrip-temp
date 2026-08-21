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


