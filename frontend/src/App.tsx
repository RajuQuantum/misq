import React, { useEffect, useMemo, useState } from 'react';
import GateTile from './components/GateTile';
import QubitLine from './components/QubitLine';
import ControlBar from './components/ControlBar';
import RotateHint from './components/RotateHint';
import MeasureButton from './components/MeasureButton';
import type { GateType, QuantumState, TrialResponse } from './types';
import {
  applyGate,
  createSession,
  fetchState,
  hardReset,
  measure,
  resetQubit,
  runTrials,
} from './api/client';

const gateDescriptions: Record<GateType, string> = {
  X: 'Flip',
  H: 'Superposition',
  CNOT: 'Entangle',
};

type LedState = {
  Q1: 0 | 1;
  Q2: 0 | 1;
};

type BlinkState = {
  Q1: boolean;
  Q2: boolean;
};

const defaultBlink: BlinkState = { Q1: false, Q2: false };
const defaultLed: LedState = { Q1: 0, Q2: 0 };

const App: React.FC = () => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [quantumState, setQuantumState] = useState<QuantumState | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [gateAura, setGateAura] = useState<Record<GateType, boolean>>({ X: false, H: false, CNOT: false });
  const [ledValues, setLedValues] = useState<LedState>(defaultLed);
  const [ledBlink, setLedBlink] = useState<BlinkState>(defaultBlink);
  const [trialsResult, setTrialsResult] = useState<TrialResponse | null>(null);
  const [loadingTrials, setLoadingTrials] = useState(false);
  const [isPortrait, setIsPortrait] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      if (typeof window !== 'undefined') {
        setIsPortrait(window.innerHeight > window.innerWidth);
      }
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    const bootstrap = async () => {
      try {
        setIsLoading(true);
        const { session_id, state } = await createSession();
        setSessionId(session_id);
        setQuantumState(state);
        setLedValues(defaultLed);
      } catch (err) {
        console.error(err);
        setError('Failed to create a new session. Please reload.');
      } finally {
        setIsLoading(false);
      }
    };

    bootstrap();
  }, []);

  const triggerGateAura = (gate: GateType) => {
    setGateAura((prev) => ({ ...prev, [gate]: true }));
    setTimeout(() => {
      setGateAura((prev) => ({ ...prev, [gate]: false }));
    }, 1200);
  };

  const triggerLedBlink = (qubit: 'Q1' | 'Q2', value: 0 | 1) => {
    setLedValues((prev) => {
      if (prev[qubit] === value) {
        return prev;
      }
      return { ...prev, [qubit]: value };
    });
    setLedBlink((prev) => ({ ...prev, [qubit]: true }));
    setTimeout(() => {
      setLedBlink((prev) => ({ ...prev, [qubit]: false }));
    }, 600);
  };

  const handleError = (message: string) => {
    setError(message);
    setTimeout(() => setError(null), 4000);
  };

  const guardSession = () => {
    if (!sessionId) {
      throw new Error('Session not ready');
    }
    return sessionId;
  };

  const handleGateClick = async (gate: GateType) => {
    try {
      const sid = guardSession();
      setBusyAction(`gate-${gate}`);
      triggerGateAura(gate);
      const state = await applyGate(sid, gate);
      setQuantumState(state);
    } catch (err) {
      console.error(err);
      handleError('Failed to apply gate.');
    } finally {
      setBusyAction(null);
    }
  };

  const handleMeasure = async (scope: 'Q1' | 'Q2' | 'BOTH') => {
    try {
      const sid = guardSession();
      setBusyAction(`measure-${scope}`);
      const result = await measure(sid, scope);
      setQuantumState(result.state);
      if (scope === 'BOTH') {
        triggerLedBlink('Q1', result.outcome.Q1);
        triggerLedBlink('Q2', result.outcome.Q2);
      } else {
        triggerLedBlink(scope, result.outcome[scope]);
      }
    } catch (err) {
      console.error(err);
      handleError('Measurement failed.');
    } finally {
      setBusyAction(null);
    }
  };

  const handleReset = async (qubit: 'Q1' | 'Q2') => {
    try {
      const sid = guardSession();
      setBusyAction(`reset-${qubit}`);
      const state = await resetQubit(sid, qubit);
      setQuantumState(state);
      triggerLedBlink(qubit, 0);
    } catch (err) {
      console.error(err);
      handleError('Reset failed.');
    } finally {
      setBusyAction(null);
    }
  };

  const handleHardReset = async () => {
    try {
      const sid = guardSession();
      setBusyAction('reset-hard');
      const state = await hardReset(sid);
      setQuantumState(state);
      triggerLedBlink('Q1', 0);
      triggerLedBlink('Q2', 0);
      setTrialsResult(null);
    } catch (err) {
      console.error(err);
      handleError('Hard reset failed.');
    } finally {
      setBusyAction(null);
    }
  };

  const handleTrials = async (scope: 'Q1' | 'Q2' | 'BOTH', n: number) => {
    try {
      const sid = guardSession();
      setLoadingTrials(true);
      const result = await runTrials(sid, scope, n);
      setTrialsResult(result);
    } catch (err) {
      console.error(err);
      handleError('Trials failed.');
    } finally {
      setLoadingTrials(false);
    }
  };

  useEffect(() => {
    if (!sessionId) {
      return;
    }
    const syncState = async () => {
      try {
        const state = await fetchState(sessionId);
        setQuantumState(state);
      } catch (err) {
        console.warn('Unable to refresh state', err);
      }
    };
    const interval = setInterval(syncState, 20000);
    return () => clearInterval(interval);
  }, [sessionId]);

  useEffect(() => {
    if (!quantumState) {
      return;
    }
    const updates: Partial<LedState> = {};
    (['Q1', 'Q2'] as const).forEach((qubit) => {
      const value = quantumState.last_measurement[qubit];
      if (value === 0 || value === 1) {
        updates[qubit] = value;
      }
    });
    if (Object.keys(updates).length > 0) {
      setLedValues((prev) => ({ ...prev, ...updates }));
    }
  }, [quantumState]);

  const amplitudeList = useMemo(() => {
    if (!quantumState) return [];
    return Object.entries(quantumState.vector).map(([basis, amplitude]) => ({
      basis,
      magnitude: Math.sqrt(amplitude.real ** 2 + amplitude.imag ** 2).toFixed(3),
      real: amplitude.real.toFixed(3),
      imag: amplitude.imag.toFixed(3),
    }));
  }, [quantumState]);

  const busy = Boolean(busyAction) || isLoading;

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800">
      {isPortrait && <RotateHint />}
      <div className="mx-auto flex min-h-screen max-w-6xl flex-col gap-6 px-6 py-10">
        <header className="flex flex-col gap-2 text-center md:text-left">
          <h1 className="text-3xl font-bold text-slate-100">Quantum Circuit Playground</h1>
          <p className="text-sm text-slate-300">
            Toggle gates to evolve the two-qubit system. Apply H then CNOT to explore entanglement and verify with trials.
          </p>
        </header>

        {error && (
          <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-4 text-sm text-red-200 shadow-lg">
            {error}
          </div>
        )}

        <ControlBar
          onReset={handleReset}
          onHardReset={handleHardReset}
          onRunTrials={handleTrials}
          trialsResult={trialsResult}
          disabled={busy}
          loadingTrials={loadingTrials}
        />

        <main className="flex flex-1 flex-col gap-6">
          <div className="flex flex-col gap-6 rounded-3xl border border-slate-700 bg-slate-900/70 p-6 shadow-2xl">
            <QubitLine
              qubit="Q1"
              gates={
                <div className="flex items-center gap-6">
                  <GateTile
                    gate="X"
                    label="G1"
                    description={gateDescriptions.X}
                    active={gateAura.X}
                    disabled={busy}
                    onClick={handleGateClick}
                  />
                  <GateTile
                    gate="H"
                    label="G2"
                    description={gateDescriptions.H}
                    active={gateAura.H}
                    disabled={busy}
                    onClick={handleGateClick}
                  />
                </div>
              }
              ledValue={ledValues.Q1}
              blinking={ledBlink.Q1}
              onMeasure={(scope) => handleMeasure(scope)}
              disabled={busy}
            />

            <div className="flex flex-col items-center gap-2">
              <GateTile
                gate="CNOT"
                label="G3"
                description={gateDescriptions.CNOT}
                active={gateAura.CNOT}
                disabled={busy}
                onClick={handleGateClick}
              />
              <MeasureButton qubit="BOTH" onMeasure={handleMeasure} disabled={busy} />
            </div>

            <QubitLine
              qubit="Q2"
              gates={<div className="text-xs text-slate-500">Q2 target line</div>}
              ledValue={ledValues.Q2}
              blinking={ledBlink.Q2}
              onMeasure={(scope) => handleMeasure(scope)}
              disabled={busy}
            />
          </div>

          <section className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-2xl border border-slate-700 bg-slate-900/70 p-5">
              <h2 className="text-lg font-semibold text-slate-200">State Vector</h2>
              <table className="mt-4 w-full table-fixed border-separate border-spacing-y-2 text-sm text-slate-200">
                <thead>
                  <tr className="text-xs uppercase tracking-wide text-slate-400">
                    <th className="text-left">Basis</th>
                    <th className="text-left">Real</th>
                    <th className="text-left">Imag</th>
                    <th className="text-left">|Amp|</th>
                  </tr>
                </thead>
                <tbody>
                  {amplitudeList.map((amp) => (
                    <tr key={amp.basis} className="rounded-lg bg-slate-800/60">
                      <td className="rounded-l-lg px-3 py-2 font-mono text-quantum-accent">|{amp.basis}⟩</td>
                      <td className="px-3 py-2 font-mono">{amp.real}</td>
                      <td className="px-3 py-2 font-mono">{amp.imag}</td>
                      <td className="rounded-r-lg px-3 py-2 font-mono">{amp.magnitude}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="rounded-2xl border border-slate-700 bg-slate-900/70 p-5">
              <h2 className="text-lg font-semibold text-slate-200">Session</h2>
              <ul className="mt-3 space-y-2 text-sm text-slate-300">
                <li>
                  <span className="font-semibold text-slate-200">Session ID:</span> {sessionId ?? '…'}
                </li>
                <li>
                  <span className="font-semibold text-slate-200">Collapsed flags:</span>{' '}
                  {quantumState
                    ? `Q1: ${quantumState.collapsed.Q1 ? 'Yes' : 'No'}, Q2: ${quantumState.collapsed.Q2 ? 'Yes' : 'No'}`
                    : '…'}
                </li>
                <li>
                  <span className="font-semibold text-slate-200">Last measurement:</span>{' '}
                  {quantumState
                    ? `Q1: ${quantumState.last_measurement.Q1 ?? '—'}, Q2: ${quantumState.last_measurement.Q2 ?? '—'}`
                    : '…'}
                </li>
              </ul>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
};

export default App;
