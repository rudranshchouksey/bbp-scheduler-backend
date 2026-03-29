from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.database import init_db
from app.routers import schedule, unit_operations, batches
from app.exceptions.handlers import validation_exception_handler, generic_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="BBP Bioprocess Scheduler API",
        description="Batch scheduling for Boston Bioprocess manufacturing workflows.",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.APP_ENV != "production" else None,
        redoc_url="/redoc" if settings.APP_ENV != "production" else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    app.include_router(schedule.router)
    app.include_router(unit_operations.router)
    app.include_router(batches.router, prefix="/api")

    @app.get("/health", tags=["Health"])
    def health():
        return {"status": "ok", "env": settings.APP_ENV}

    return app


app = create_app()