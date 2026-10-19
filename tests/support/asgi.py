import json
from typing import Any

from fastapi import FastAPI
from starlette.types import Message, Scope


async def post_json(
    app: FastAPI,
    path: str,
    payload: dict[str, Any],
    *,
    request_headers: list[tuple[bytes, bytes]] | None = None,
    client: tuple[str, int] | None = ("127.0.0.1", 12345),
) -> tuple[int, dict[str, Any]]:
    status, body, _ = await post_json_with_headers(
        app,
        path,
        payload,
        request_headers=request_headers,
        client=client,
    )
    return status, body


async def post_json_with_headers(
    app: FastAPI,
    path: str,
    payload: dict[str, Any],
    *,
    request_headers: list[tuple[bytes, bytes]] | None = None,
    client: tuple[str, int] | None = ("127.0.0.1", 12345),
) -> tuple[int, dict[str, Any], list[tuple[bytes, bytes]]]:
    body = json.dumps(payload).encode()
    scope: Scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "root_path": "",
        "headers": [(b"content-type", b"application/json"), *(request_headers or [])],
        "client": client,
        "server": ("testserver", 80),
    }
    messages: list[Message] = []
    received = False

    async def receive() -> Message:
        nonlocal received
        if received:
            return {"type": "http.disconnect"}
        received = True
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message: Message) -> None:
        messages.append(message)

    await app(scope, receive, send)
    response_start = next(message for message in messages if message["type"] == "http.response.start")
    status = response_start["status"]
    content = b"".join(message.get("body", b"") for message in messages if message["type"] == "http.response.body")
    return status, json.loads(content) if content else {}, response_start.get("headers", [])


async def get_json_with_headers(
    app: FastAPI,
    path: str,
    *,
    request_headers: list[tuple[bytes, bytes]] | None = None,
    client: tuple[str, int] | None = ("127.0.0.1", 12345),
) -> tuple[int, dict[str, Any], list[tuple[bytes, bytes]]]:
    scope: Scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "root_path": "",
        "headers": request_headers or [],
        "client": client,
        "server": ("testserver", 80),
    }
    messages: list[Message] = []
    received = False

    async def receive() -> Message:
        nonlocal received
        if received:
            return {"type": "http.disconnect"}
        received = True
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: Message) -> None:
        messages.append(message)

    await app(scope, receive, send)
    response_start = next(message for message in messages if message["type"] == "http.response.start")
    status = response_start["status"]
    content = b"".join(message.get("body", b"") for message in messages if message["type"] == "http.response.body")
    return status, json.loads(content), response_start.get("headers", [])
