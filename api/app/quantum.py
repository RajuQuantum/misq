from __future__ import annotations

from typing import Dict, Tuple

import numpy as np

from .utils import BASIS_STATES, normalize, probabilities_from_amplitudes, sample_index

H = (1 / np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=np.complex128)
X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
I2 = np.eye(2, dtype=np.complex128)

H_Q1 = np.kron(H, I2)
X_Q1 = np.kron(X, I2)

CNOT = np.array(
    [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0],
    ],
    dtype=np.complex128,
)

GATE_MATRICES = {
    "H": H_Q1,
    "X": X_Q1,
    "CNOT": CNOT,
}


def initial_state() -> np.ndarray:
    return np.array([1, 0, 0, 0], dtype=np.complex128)


def apply_gate_to_state(state: np.ndarray, gate: str) -> np.ndarray:
    if gate not in GATE_MATRICES:
        raise ValueError(f"Unsupported gate: {gate}")
    matrix = GATE_MATRICES[gate]
    new_state = matrix @ state
    return normalize(new_state)


def measure_qubit(state: np.ndarray, qubit: str) -> Tuple[int, np.ndarray]:
    if qubit not in ("Q1", "Q2"):
        raise ValueError("qubit must be Q1 or Q2")

    amplitudes = state.copy()
    if qubit == "Q1":
        prob0 = abs(amplitudes[0]) ** 2 + abs(amplitudes[1]) ** 2
        prob1 = abs(amplitudes[2]) ** 2 + abs(amplitudes[3]) ** 2
        probabilities = [prob0, prob1]
        choice = sample_index(probabilities)
        if choice == 0:
            collapsed = np.array([amplitudes[0], amplitudes[1], 0, 0], dtype=np.complex128)
        else:
            collapsed = np.array([0, 0, amplitudes[2], amplitudes[3]], dtype=np.complex128)
    else:
        prob0 = abs(amplitudes[0]) ** 2 + abs(amplitudes[2]) ** 2
        prob1 = abs(amplitudes[1]) ** 2 + abs(amplitudes[3]) ** 2
        probabilities = [prob0, prob1]
        choice = sample_index(probabilities)
        if choice == 0:
            collapsed = np.array([amplitudes[0], 0, amplitudes[2], 0], dtype=np.complex128)
        else:
            collapsed = np.array([0, amplitudes[1], 0, amplitudes[3]], dtype=np.complex128)

    if probabilities[choice] == 0:
        collapsed = np.zeros_like(collapsed)
        if qubit == "Q1":
            collapsed[0 if choice == 0 else 2] = 1
        else:
            collapsed[0 if choice == 0 else 1] = 1
    normalized = normalize(collapsed)
    return choice, normalized


def measure_both(state: np.ndarray) -> Tuple[Dict[str, int], np.ndarray]:
    amplitudes = state.copy()
    probabilities = probabilities_from_amplitudes(amplitudes)
    index = sample_index(probabilities)
    basis = BASIS_STATES[index]
    collapsed = np.zeros_like(amplitudes)
    collapsed[index] = 1.0
    collapsed = normalize(collapsed)
    return {"Q1": int(basis[0]), "Q2": int(basis[1])}, collapsed


def reset_qubit(state: np.ndarray, qubit: str) -> np.ndarray:
    amplitudes = state.copy()
    if qubit == "Q1":
        new00 = amplitudes[0] + amplitudes[2]
        new01 = amplitudes[1] + amplitudes[3]
        collapsed = np.array([new00, new01, 0, 0], dtype=np.complex128)
    elif qubit == "Q2":
        new00 = amplitudes[0] + amplitudes[1]
        new10 = amplitudes[2] + amplitudes[3]
        collapsed = np.array([new00, 0, new10, 0], dtype=np.complex128)
    else:
        raise ValueError("qubit must be Q1 or Q2")
    norm = np.linalg.norm(collapsed)
    if np.isclose(norm, 0.0):
        collapsed = initial_state()
    return normalize(collapsed)


def hard_reset() -> np.ndarray:
    return initial_state()


def run_trials(state: np.ndarray, scope: str, n: int) -> Tuple[Dict[str, int], Dict[str, float]]:
    if n <= 0:
        raise ValueError("Number of trials must be positive")
    counts: Dict[str, int] = {}
    for _ in range(n):
        working_state = state.copy()
        if scope == "BOTH":
            outcome, _ = measure_both(working_state)
            key = f"{outcome['Q1']}{outcome['Q2']}"
        elif scope in ("Q1", "Q2"):
            result, _ = measure_qubit(working_state, scope)
            key = str(result)
        else:
            raise ValueError("Invalid scope for trials")
        counts[key] = counts.get(key, 0) + 1
    freqs = {key: value / n for key, value in counts.items()}
    return counts, freqs
