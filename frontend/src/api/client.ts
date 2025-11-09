import axios from 'axios';
import type { GateType, QubitId, QuantumState, TrialResponse } from '../types';

type MeasureScope = QubitId | 'BOTH';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE ?? '/api',
  timeout: 8000,
});

export const createSession = async () => {
  const { data } = await api.post<{ session_id: string; state: QuantumState }>('/session/new');
  return data;
};

export const fetchState = async (sessionId: string) => {
  const { data } = await api.get<{ state: QuantumState }>(`/state/${sessionId}`);
  return data.state;
};

export const applyGate = async (sessionId: string, gate: GateType) => {
  const { data } = await api.post<{ state: QuantumState }>('/gate/apply', { session_id: sessionId, gate });
  return data.state;
};

export const measure = async (sessionId: string, qubit: MeasureScope) => {
  const { data } = await api.post<{ outcome: { Q1: 0 | 1; Q2: 0 | 1 }; state: QuantumState }>('/measure', {
    session_id: sessionId,
    qubit,
  });
  return data;
};

export const resetQubit = async (sessionId: string, qubit: QubitId) => {
  const { data } = await api.post<{ state: QuantumState }>('/reset', {
    session_id: sessionId,
    qubit,
  });
  return data.state;
};

export const hardReset = async (sessionId: string) => {
  const { data } = await api.post<{ state: QuantumState }>('/reset/hard', {
    session_id: sessionId,
  });
  return data.state;
};

export const runTrials = async (sessionId: string, qubit: MeasureScope, n: number) => {
  const { data } = await api.post<TrialResponse>('/trials', {
    session_id: sessionId,
    qubit,
    n,
  });
  return data;
};

export default api;
