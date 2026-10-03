"""
FoodFlow Analytics FastAPI Application Entrypoint.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.backend.config import settings
from src.backend.routers import health, analytics, explorer

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-quality REST API analytics backend for FoodFlow Analytics dashboard."
)

# CORS Middleware Configuration for React Dev Servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers under /api
app.include_router(health.router, prefix=settings.API_PREFIX)
app.include_router(analytics.router, prefix=settings.API_PREFIX)
app.include_router(explorer.router, prefix=settings.API_PREFIX)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": f"Internal server error: {str(exc)}"}
    )


@app.get("/")
def root():
    return {
        "message": "Welcome to FoodFlow Analytics API Backend",
        "health_check": f"{settings.API_PREFIX}/health",
        "docs_url": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.backend.main:app", host="0.0.0.0", port=8000, reload=True)
