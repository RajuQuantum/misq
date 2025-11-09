"""Simplified FastAPI substitute supporting unit tests without network access."""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Tuple, get_type_hints

from .pydantic_stub import BaseModel


class HTTPException(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


@dataclass
class Route:
    method: str
    path: str
    handler: Callable


class FastAPI:
    def __init__(self, title: str = "", version: str = ""):
        self.title = title
        self.version = version
        self._routes: List[Route] = []
        self._startup_handlers: List[Callable[[], None]] = []
        self._middlewares: List[Tuple[Any, Dict[str, Any]]] = []

    def add_middleware(self, middleware_cls: Any, **options: Any) -> None:
        self._middlewares.append((middleware_cls, options))

    def on_event(self, event_type: str) -> Callable[[Callable], Callable]:
        def decorator(func: Callable) -> Callable:
            if event_type == "startup":
                self._startup_handlers.append(func)
            return func

        return decorator

    def _register(self, method: str, path: str, handler: Callable) -> Callable:
        self._routes.append(Route(method=method.upper(), path=path, handler=handler))
        return handler

    def get(self, path: str, response_model: Optional[Any] = None) -> Callable:
        def decorator(func: Callable) -> Callable:
            return self._register("GET", path, func)

        return decorator

    def post(self, path: str, response_model: Optional[Any] = None) -> Callable:
        def decorator(func: Callable) -> Callable:
            return self._register("POST", path, func)

        return decorator

    def startup(self) -> None:
        for handler in self._startup_handlers:
            handler()

    def _match(self, method: str, path: str) -> Tuple[Callable, Dict[str, str]]:
        for route in self._routes:
            if route.method != method.upper():
                continue
            params = _match_path(route.path, path)
            if params is not None:
                return route.handler, params
        raise HTTPException(status_code=404, detail="Not Found")


class CORSMiddleware:
    def __init__(self, *args: Any, **kwargs: Any):
        self.options = kwargs


class Response:
    def __init__(self, status_code: int, data: Any):
        self.status_code = status_code
        self._data = data

    def json(self) -> Any:
        return self._data


class TestClient:
    __test__ = False

    def __init__(self, app: FastAPI):
        self.app = app
        self.app.startup()

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Response:
        return self._request("GET", path, params=params)

    def post(self, path: str, json: Optional[Dict[str, Any]] = None) -> Response:
        return self._request("POST", path, json=json)

    def _request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None) -> Response:
        try:
            handler, path_params = self.app._match(method, path)
        except HTTPException as exc:
            return Response(exc.status_code, {"detail": exc.detail})
        try:
            result = _invoke_handler(handler, path_params, json or {}, params or {})
            return Response(200, _serialize(result))
        except HTTPException as exc:
            return Response(exc.status_code, {"detail": exc.detail})


def _match_path(template: str, path: str) -> Optional[Dict[str, str]]:
    template_parts = [part for part in template.strip("/").split("/") if part]
    path_parts = [part for part in path.strip("/").split("/") if part]
    if len(template_parts) != len(path_parts):
        return None
    params: Dict[str, str] = {}
    for expected, actual in zip(template_parts, path_parts):
        if expected.startswith("{") and expected.endswith("}"):
            key = expected[1:-1]
            params[key] = actual
        elif expected != actual:
            return None
    return params


def _invoke_handler(handler: Callable, path_params: Dict[str, str], body: Dict[str, Any], query: Dict[str, Any]) -> Any:
    signature = inspect.signature(handler)
    kwargs: Dict[str, Any] = {}
    type_hints = get_type_hints(handler)
    for name, parameter in signature.parameters.items():
        annotation = type_hints.get(name, parameter.annotation)
        if name in path_params:
            kwargs[name] = _convert_type(path_params[name], annotation)
            continue
        if annotation is inspect._empty:
            kwargs[name] = body if body else query
            continue
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            kwargs[name] = _parse_body(body, annotation)
            continue
        if name == "payload":
            kwargs[name] = _parse_body(body, annotation)
        else:
            kwargs[name] = body if body else query
    return handler(**kwargs)


def _convert_type(value: str, annotation: Any) -> Any:
    if annotation in (int, float, bool):
        return annotation(value)
    return value


def _parse_body(body: Dict[str, Any], annotation: Any) -> Any:
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return annotation(**body)
    return body


def _serialize(obj: Any) -> Any:
    if isinstance(obj, BaseModel):
        return obj.dict()
    if isinstance(obj, list):
        return [_serialize(item) for item in obj]
    if isinstance(obj, dict):
        return {key: _serialize(value) for key, value in obj.items()}
    return obj


def build_fastapi_modules() -> Dict[str, ModuleType]:
    fastapi_module = ModuleType("fastapi")
    fastapi_module.FastAPI = FastAPI
    fastapi_module.HTTPException = HTTPException
    fastapi_module.middleware = ModuleType("fastapi.middleware")
    cors_module = ModuleType("fastapi.middleware.cors")
    cors_module.CORSMiddleware = CORSMiddleware
    fastapi_module.middleware.cors = cors_module
    testclient_module = ModuleType("fastapi.testclient")
    testclient_module.TestClient = TestClient
    return {
        "fastapi": fastapi_module,
        "fastapi.middleware": fastapi_module.middleware,
        "fastapi.middleware.cors": cors_module,
        "fastapi.testclient": testclient_module,
    }
