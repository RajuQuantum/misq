from __future__ import annotations

from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import db, quantum
from .models import (
    GateRequest,
    HardResetRequest,
    MeasureRequest,
    MeasureResponse,
    ResetRequest,
    SessionResponse,
    StateResponse,
    TrialsRequest,
    TrialsResponse,
)
from .utils import vector_to_dict

app = FastAPI(title="Quantum Circuit Playground API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    db.init_db()


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/session/new", response_model=SessionResponse)
def create_session_route() -> SessionResponse:
    return db.create_session()


@app.get("/api/state/{session_id}", response_model=StateResponse)
def get_state(session_id: str) -> StateResponse:
    try:
        _, state_model = db.fetch_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found") from None
    return StateResponse(state=state_model)


@app.post("/api/gate/apply", response_model=StateResponse)
def apply_gate_route(payload: GateRequest) -> StateResponse:
    try:
        vector, _ = db.fetch_session(payload.session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found") from None

    new_vector = quantum.apply_gate_to_state(vector, payload.gate)
    collapsed = {"Q1": False, "Q2": False}
    last_measurement = {"Q1": None, "Q2": None}
    state_model = db.update_session_state(payload.session_id, new_vector, collapsed, last_measurement)
    db.log_action(
        payload.session_id,
        "GATE",
        {"gate": payload.gate, "state": vector_to_dict(new_vector)},
    )
    return StateResponse(state=state_model)


@app.post("/api/measure", response_model=MeasureResponse)
def measure_route(payload: MeasureRequest) -> MeasureResponse:
    try:
        vector, current_state = db.fetch_session(payload.session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found") from None

    if payload.qubit == "BOTH":
        outcome, collapsed_vector = quantum.measure_both(vector)
        collapsed_flags = {"Q1": True, "Q2": True}
        last_measurement = {"Q1": outcome["Q1"], "Q2": outcome["Q2"]}
    else:
        result, collapsed_vector = quantum.measure_qubit(vector, payload.qubit)
        outcome = {"Q1": current_state.last_measurement.get("Q1"), "Q2": current_state.last_measurement.get("Q2")}
        outcome[payload.qubit] = result
        collapsed_flags = {"Q1": False, "Q2": False}
        collapsed_flags[payload.qubit] = True
        last_measurement = {"Q1": None, "Q2": None}
        last_measurement[payload.qubit] = result
    state_model = db.update_session_state(payload.session_id, collapsed_vector, collapsed_flags, last_measurement)
    db.log_action(
        payload.session_id,
        "MEASURE",
        {"scope": payload.qubit, "outcome": outcome},
    )
    return MeasureResponse(outcome=outcome, state=state_model)


@app.post("/api/reset", response_model=StateResponse)
def reset_route(payload: ResetRequest) -> StateResponse:
    try:
        vector, _ = db.fetch_session(payload.session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found") from None

    new_vector = quantum.reset_qubit(vector, payload.qubit)
    collapsed_flags = {"Q1": False, "Q2": False}
    last_measurement = {"Q1": None, "Q2": None}
    last_measurement[payload.qubit] = 0
    state_model = db.update_session_state(payload.session_id, new_vector, collapsed_flags, last_measurement)
    db.log_action(
        payload.session_id,
        "RESET",
        {"qubit": payload.qubit},
    )
    return StateResponse(state=state_model)


@app.post("/api/reset/hard", response_model=StateResponse)
def hard_reset_route(payload: HardResetRequest) -> StateResponse:
    try:
        db.fetch_session(payload.session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found") from None

    new_vector = quantum.hard_reset()
    collapsed_flags = {"Q1": False, "Q2": False}
    last_measurement = {"Q1": 0, "Q2": 0}
    state_model = db.update_session_state(payload.session_id, new_vector, collapsed_flags, last_measurement)
    db.log_action(payload.session_id, "HARD_RESET", {})
    return StateResponse(state=state_model)


@app.post("/api/trials", response_model=TrialsResponse)
def trials_route(payload: TrialsRequest) -> TrialsResponse:
    try:
        vector, _ = db.fetch_session(payload.session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found") from None

    counts, freqs = quantum.run_trials(vector, payload.qubit, payload.n)
    db.log_trials(payload.session_id, payload.qubit, payload.n, counts, freqs)
    return TrialsResponse(counts=counts, freqs=freqs)
