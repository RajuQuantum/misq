"""Install lightweight compatibility shims when third-party packages are unavailable."""

from __future__ import annotations

import sys
from importlib import import_module
from types import ModuleType

from . import fastapi_stub, numpy_stub, pydantic_stub


def _ensure_module(name: str, factory) -> None:
    try:
        import_module(name)
    except ModuleNotFoundError:
        module = factory()
        if isinstance(module, ModuleType):
            sys.modules[name] = module
        elif isinstance(module, dict):
            for key, value in module.items():
                sys.modules[key] = value
        else:
            raise TypeError("Stub factory must return ModuleType or mapping")


def ensure_dependencies() -> None:
    """Install numpy, pydantic, and fastapi shims if missing."""
    _ensure_module("numpy", numpy_stub.build_numpy_module)
    _ensure_module("numpy.linalg", numpy_stub.build_numpy_linalg_module)
    _ensure_module("pydantic", pydantic_stub.build_pydantic_module)
    try:
        import_module("fastapi")
    except ModuleNotFoundError:
        fastapi_modules = fastapi_stub.build_fastapi_modules()
        for key, value in fastapi_modules.items():
            if key not in sys.modules:
                sys.modules[key] = value
