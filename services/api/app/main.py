from fastapi import FastAPI
from mangum import Mangum

app = FastAPI(
    title="APIverse",
    description="API Management Platform",
    version="0.1.0"
)

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
