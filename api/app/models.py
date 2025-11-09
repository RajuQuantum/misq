from __future__ import annotations

from typing import Dict, Literal, Optional

from pydantic import BaseModel, Field, validator

from .utils import BASIS_STATES


class ComplexAmplitude(BaseModel):
    real: float
    imag: float


class QuantumStateModel(BaseModel):
    vector: Dict[str, ComplexAmplitude]
    collapsed: Dict[str, bool]
    last_measurement: Dict[str, Optional[int]]

    @validator('vector')
    def validate_basis(cls, value: Dict[str, ComplexAmplitude]):
        missing = [basis for basis in BASIS_STATES if basis not in value]
        if missing:
            raise ValueError(f'Missing amplitudes for basis states: {missing}')
        return value


class SessionResponse(BaseModel):
    session_id: str = Field(..., alias='session_id')
    state: QuantumStateModel

    class Config:
        allow_population_by_field_name = True


class StateResponse(BaseModel):
    state: QuantumStateModel


class GateRequest(BaseModel):
    session_id: str
    gate: Literal['X', 'H', 'CNOT']


class MeasureRequest(BaseModel):
    session_id: str
    qubit: Literal['Q1', 'Q2', 'BOTH']


class MeasureResponse(BaseModel):
    outcome: Dict[str, int]
    state: QuantumStateModel


class ResetRequest(BaseModel):
    session_id: str
    qubit: Literal['Q1', 'Q2']


class HardResetRequest(BaseModel):
    session_id: str


class TrialsRequest(BaseModel):
    session_id: str
    qubit: Literal['Q1', 'Q2', 'BOTH']
    n: int


class TrialsResponse(BaseModel):
    counts: Dict[str, int]
    freqs: Dict[str, float]
