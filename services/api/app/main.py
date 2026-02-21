from fastapi import FastAPI
from mangum import Mangum
from app.routers import auth

app = FastAPI(
    title="APIverse",
    description="API Management Platform",
    version="0.1.0"
)

app.include_router(auth.router)

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

handler = Mangum(app)
