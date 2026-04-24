from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(self, code: str, message: str, detail: str | None = None, status_code: int = 400):
        super().__init__(
            status_code=status_code,
            detail={"code": code, "message": message, "detail": detail or ""},
        )


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "invalid or expired token"):
        super().__init__(
            code="AUTH_401",
            message="Unauthorized",
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class NotFoundException(AppException):
    def __init__(self, detail: str = "resource not found"):
        super().__init__(
            code="NOT_FOUND",
            message="Not Found",
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class TaskNotReadyException(AppException):
    def __init__(self, detail: str = "report task is not completed"):
        super().__init__(
            code="TASK_NOT_READY",
            message="Task Not Ready",
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
        )


class InternalServerException(AppException):
    def __init__(self, detail: str = "internal server error"):
        super().__init__(
            code="INTERNAL_ERROR",
            message="Internal Server Error",
            detail=detail,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
