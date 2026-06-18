from main import app
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code)


@app.exception_handler(ConnectionResetError)
async def ConnectionResetError_handler(request, exc):
    return JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code)
