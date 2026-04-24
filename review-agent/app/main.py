from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers.auth import router as auth_router
from app.routers.reports import router as reports_router
from app.services.bootstrap import bootstrap_auth_data
from app.utils.exceptions import AppException


@asynccontextmanager
async def lifespan(_: FastAPI):
    await bootstrap_auth_data()
    yield


app = FastAPI(title="review-agent", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(reports_router)


@app.exception_handler(AppException)
async def app_exception_handler(_, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content=exc.detail)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"code": "VALIDATION_ERROR", "message": "Validation Error", "detail": str(exc)},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, dict) else str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": "HTTP_ERROR", "message": "HTTP Error", "detail": detail},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"code": "INTERNAL_ERROR", "message": "Internal Server Error", "detail": str(exc)},
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
