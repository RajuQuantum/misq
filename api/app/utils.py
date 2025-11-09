from __future__ import annotations

import json
from secrets import SystemRandom
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np

BASIS_STATES: Tuple[str, ...] = ("00", "01", "10", "11")

_rng = SystemRandom()


def get_rng() -> SystemRandom:
    return _rng


def normalize(vector: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vector)
    if norm == 0:
        raise ValueError("State vector cannot be zero")
    return vector / norm


def vector_to_dict(vector: np.ndarray) -> Dict[str, Dict[str, float]]:
    return {
        basis: {"real": float(np.real(value)), "imag": float(np.imag(value))}
        for basis, value in zip(BASIS_STATES, vector)
    }


def dict_to_vector(data: Dict[str, Dict[str, float]]) -> np.ndarray:
    return np.array(
        [complex(data[basis]["real"], data[basis]["imag"]) for basis in BASIS_STATES],
        dtype=np.complex128,
    )


def serialize_state(vector: np.ndarray) -> str:
    payload = vector_to_dict(vector)
    return json.dumps(payload)


def deserialize_state(payload: str) -> np.ndarray:
    data = json.loads(payload)
    ordered = {basis: data[basis] for basis in BASIS_STATES}
    return dict_to_vector(ordered)


def sample_index(probabilities: Sequence[float]) -> int:
    total = sum(probabilities)
    if total <= 0:
        raise ValueError("Invalid probability distribution")
    normalized = [p / total for p in probabilities]
    threshold = get_rng().random()
    cumulative = 0.0
    for index, probability in enumerate(normalized):
        cumulative += probability
        if threshold <= cumulative:
            return index
    return len(probabilities) - 1


def probabilities_from_amplitudes(vector: np.ndarray) -> List[float]:
    return [float(abs(value) ** 2) for value in vector]
