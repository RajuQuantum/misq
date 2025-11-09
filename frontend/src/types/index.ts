export type Complex = {
  real: number;
  imag: number;
};

export type BasisState = '00' | '01' | '10' | '11';

export interface QuantumState {
  vector: Record<BasisState, Complex>;
  collapsed: {
    Q1: boolean;
    Q2: boolean;
  };
  last_measurement: {
    Q1: 0 | 1 | null;
    Q2: 0 | 1 | null;
  };
}

export interface SessionState {
  sessionId: string;
  state: QuantumState;
}

export type GateType = 'X' | 'H' | 'CNOT';

export type QubitId = 'Q1' | 'Q2';

export interface TrialResponse {
  counts: Record<string, number>;
  freqs: Record<string, number>;
}
