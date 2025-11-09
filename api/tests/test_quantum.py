import math

import numpy as np

from app import quantum
from app.utils import probabilities_from_amplitudes


def test_h_gate_probability_balanced():
    state = quantum.initial_state()
    state = quantum.apply_gate_to_state(state, 'H')
    probabilities = probabilities_from_amplitudes(state)
    assert math.isclose(probabilities[0], 0.5, rel_tol=1e-2)
    assert math.isclose(probabilities[2], 0.5, rel_tol=1e-2)


def test_bell_state_measurement_outcomes():
    state = quantum.initial_state()
    state = quantum.apply_gate_to_state(state, 'H')
    state = quantum.apply_gate_to_state(state, 'CNOT')
    outcomes = set()
    for _ in range(50):
        outcome, _ = quantum.measure_both(state.copy())
        outcomes.add(f"{outcome['Q1']}{outcome['Q2']}")
    assert outcomes.issubset({'00', '11'})
    assert outcomes  # not empty


def test_measurement_collapses_and_normalizes():
    state = quantum.initial_state()
    state = quantum.apply_gate_to_state(state, 'H')
    result, collapsed = quantum.measure_qubit(state, 'Q1')
    assert result in (0, 1)
    norm = np.linalg.norm(collapsed)
    assert math.isclose(norm, 1.0, rel_tol=1e-9)


def test_resets_clear_entanglement():
    state = quantum.initial_state()
    state = quantum.apply_gate_to_state(state, 'H')
    state = quantum.apply_gate_to_state(state, 'CNOT')
    reset_state = quantum.reset_qubit(state, 'Q1')
    assert reset_state[2] == 0
    assert reset_state[3] == 0
    norm = np.linalg.norm(reset_state)
    assert math.isclose(norm, 1.0, rel_tol=1e-9)
