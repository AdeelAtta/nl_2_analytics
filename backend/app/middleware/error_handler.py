from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.schemas.health import ProblemDetail


def setup_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        problem = ProblemDetail(
            type="about:blank",
            title="Internal Server Error",
            status=500,
            detail=str(exc),
            instance=str(request.url),
        )
        return JSONResponse(
            status_code=500,
            content=problem.model_dump(),
        )
