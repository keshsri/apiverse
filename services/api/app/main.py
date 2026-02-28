from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.routers import auth, apis, api_keys, proxy, rate_limits

app = FastAPI(
    title="APIverse",
    description="API Management Platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    root_path="/dev"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(apis.router)
app.include_router(api_keys.router)
app.include_router(rate_limits.router)
app.include_router(proxy.router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "apiverse",
        "version": "0.1.0"
    }

@app.get("/")
def root():
    return {
        "message": "Welcome to APIverse API Management Platform",
        "docs": "/docs"
    }

handler = Mangum(app, lifespan="off")
