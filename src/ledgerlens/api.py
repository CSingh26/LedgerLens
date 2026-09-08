"""Stateless local research API; request bodies are bounded before JSON parsing."""

from pathlib import Path
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from .demo import demo_request
from .provider import MAX_BYTES, ProviderError, fetch_companyfacts, parse_companyfacts
from .schemas import AnalysisRequest, FetchRequest, JsonObject
from .service import analyze


class BodyLimit:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        content = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            content.extend(message.get("body", b""))
            if len(content) > MAX_BYTES:
                await JSONResponse({"detail": "Request exceeds 10 MB"}, status_code=413)(
                    scope, receive, send
                )
                return
            if not message.get("more_body", False):
                break
        replayed = False

        async def replay() -> Message:
            nonlocal replayed
            if replayed:
                return await receive()
            replayed = True
            return {"type": "http.request", "body": bytes(content), "more_body": False}

        await self.app(scope, replay, send)


app = FastAPI(title="LedgerLens", version="0.1.0")
app.add_middleware(BodyLimit)


@app.exception_handler(RequestValidationError)
async def validation_error(_request: Request, exc: RequestValidationError) -> JSONResponse:
    # Do not echo nonfinite inputs or arbitrary error contexts into JSON responses.
    detail = [
        {"location": ".".join(map(str, error["loc"])), "message": error["msg"]}
        for error in exc.errors()
    ]
    return JSONResponse({"detail": detail}, status_code=422)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ledgerlens"}


@app.get("/api/demo")
def demo() -> JsonObject:
    return demo_request().model_dump(mode="json")


@app.post("/api/analyze")
def analysis(request: AnalysisRequest) -> JsonObject:
    try:
        return analyze(request)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/import")
async def import_facts(request: Request) -> JsonObject:
    try:
        return parse_companyfacts(await request.body())
    except ValueError as exc:
        raise HTTPException(
            status_code=422, detail="Invalid SEC companyfacts JSON: " + str(exc)[:400]
        ) from exc


@app.post("/api/fetch")
def fetch_facts(request: FetchRequest) -> JsonObject:
    try:
        return fetch_companyfacts(request.cik, request.user_agent)
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


WEB = Path(__file__).parent / "web"
app.mount("/static", StaticFiles(directory=WEB), name="static")


@app.get("/", response_class=FileResponse)
def index() -> FileResponse:
    return FileResponse(WEB / "index.html")
