"""Minimal numpy compatibility layer for offline testing."""

from __future__ import annotations

import math
from copy import deepcopy
from typing import Any, Callable, List, Sequence
from types import ModuleType


class NDArray(list):
    def __matmul__(self, other: "NDArray") -> "NDArray":
        if not isinstance(other, (list, NDArray)):
            raise TypeError("Unsupported operand type for @")
        if self and isinstance(self[0], (list, NDArray)):
            result: List[complex] = []
            for row in self:
                total = 0j
                for a, b in zip(row, other):
                    total += a * b
                result.append(total)
            return NDArray(result)
        raise TypeError("Left operand must be a matrix")

    def __truediv__(self, scalar: complex) -> "NDArray":
        return self._map(lambda value: value / scalar)

    def __mul__(self, scalar: complex) -> "NDArray":
        return self._map(lambda value: value * scalar)

    def __rmul__(self, scalar: complex) -> "NDArray":
        return self.__mul__(scalar)

    def __add__(self, other: "NDArray") -> "NDArray":
        return NDArray([
            (a + b) if not isinstance(a, (list, NDArray)) else NDArray(a) + NDArray(b)
            for a, b in zip(self, other)
        ])

    def __sub__(self, other: "NDArray") -> "NDArray":
        return NDArray([
            (a - b) if not isinstance(a, (list, NDArray)) else NDArray(a) - NDArray(b)
            for a, b in zip(self, other)
        ])

    def copy(self) -> "NDArray":
        return NDArray(deepcopy(list(self)))

    def _map(self, func: Callable[[complex], complex]) -> "NDArray":
        result: List[Any] = []
        for item in self:
            if isinstance(item, (list, NDArray)):
                result.append(NDArray(item)._map(func))
            else:
                result.append(func(item))
        return NDArray(result)


complex128 = complex


def _to_complex(value):
    return complex(value)


def array(values: Sequence, dtype=None) -> NDArray:
    if isinstance(values, NDArray):
        data = deepcopy(list(values))
    else:
        data = deepcopy(list(values))
    if data and isinstance(data[0], (list, tuple, NDArray)):
        return NDArray([array(row, dtype=dtype) for row in data])
    if dtype is complex128:
        return NDArray([_to_complex(v) for v in data])
    return NDArray(data)


def eye(n: int, dtype=None) -> NDArray:
    matrix = []
    for i in range(n):
        row = []
        for j in range(n):
            value = 1 if i == j else 0
            if dtype is complex128:
                value = complex(value)
            row.append(value)
        matrix.append(NDArray(row))
    return NDArray(matrix)


def kron(a: NDArray, b: NDArray) -> NDArray:
    result = []
    for row_a in a:
        for row_b in b:
            row = []
            for val_a in row_a:
                row.extend([val_a * val_b for val_b in row_b])
            result.append(NDArray(row))
    return NDArray(result)


def sqrt(value: float) -> float:
    return math.sqrt(value)


def zeros_like(array_like: NDArray) -> NDArray:
    if array_like and isinstance(array_like[0], (list, NDArray)):
        return NDArray([zeros_like(row) for row in array_like])
    return NDArray([0 for _ in array_like])


def zeros(length: int, dtype=None) -> NDArray:
    values = [0] * length
    if dtype is complex128:
        values = [complex(0) for _ in range(length)]
    return NDArray(values)


def real(value):
    if isinstance(value, NDArray):
        return NDArray([real(v) for v in value])
    if hasattr(value, "real"):
        return value.real
    return float(value)


def imag(value):
    if isinstance(value, NDArray):
        return NDArray([imag(v) for v in value])
    if hasattr(value, "imag"):
        return value.imag
    return 0.0


def isclose(a: float, b: float, rel_tol: float = 1e-9, abs_tol: float = 0.0) -> bool:
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


def _flatten(values: Sequence) -> List[complex]:
    flattened: List[complex] = []
    for value in values:
        if isinstance(value, (list, NDArray)):
            flattened.extend(_flatten(value))
        else:
            flattened.append(value)
    return flattened


def norm(values: Sequence) -> float:
    flattened = _flatten(values)
    return math.sqrt(sum(abs(v) ** 2 for v in flattened))


def build_numpy_module() -> ModuleType:
    module = ModuleType("numpy")
    module.array = array
    module.eye = eye
    module.kron = kron
    module.sqrt = sqrt
    module.zeros_like = zeros_like
    module.zeros = zeros
    module.real = real
    module.imag = imag
    module.isclose = isclose
    module.linalg = build_numpy_linalg_module()
    module.complex128 = complex128
    module.ndarray = NDArray
    return module


def build_numpy_linalg_module() -> ModuleType:
    module = ModuleType("numpy.linalg")
    module.norm = norm
    return module
