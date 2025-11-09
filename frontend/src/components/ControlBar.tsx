import React, { useState } from 'react';
import type { TrialResponse, QubitId } from '../types';

interface ControlBarProps {
  onReset: (qubit: QubitId) => Promise<void>;
  onHardReset: () => Promise<void>;
  onRunTrials: (scope: 'Q1' | 'Q2' | 'BOTH', n: number) => Promise<void>;
  trialsResult: TrialResponse | null;
  disabled?: boolean;
  loadingTrials?: boolean;
}

const ControlBar: React.FC<ControlBarProps> = ({ onReset, onHardReset, onRunTrials, trialsResult, disabled, loadingTrials }) => {
  const [trialScope, setTrialScope] = useState<'Q1' | 'Q2' | 'BOTH'>('Q1');
  const [trialCount, setTrialCount] = useState(1000);

  const runTrials = async () => {
    await onRunTrials(trialScope, trialCount);
  };

  return (
    <div className="flex w-full flex-col gap-4 rounded-2xl border border-slate-700 bg-slate-900/60 p-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          <button
            className="rounded-lg border border-slate-600 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
            onClick={() => onReset('Q1')}
            disabled={disabled}
          >
            Reset Q1
          </button>
          <button
            className="rounded-lg border border-slate-600 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
            onClick={() => onReset('Q2')}
            disabled={disabled}
          >
            Reset Q2
          </button>
          <button
            className="rounded-lg border border-quantum-accent bg-quantum-accent/10 px-4 py-2 text-sm font-semibold text-quantum-accent transition hover:bg-quantum-accent/20 disabled:cursor-not-allowed disabled:opacity-60"
            onClick={onHardReset}
            disabled={disabled}
          >
            Hard Reset
          </button>
        </div>
        <div className="flex items-center gap-3 text-xs text-slate-400">
          <span>Use toggles to apply gates. Reset to undo.</span>
        </div>
      </div>
      <div className="flex flex-col gap-3 rounded-xl border border-slate-700 bg-slate-900/50 p-4">
        <div className="flex flex-wrap items-center gap-4">
          <label className="flex items-center gap-2 text-sm text-slate-200">
            Scope:
            <select
              className="rounded-md border border-slate-600 bg-slate-800 px-2 py-1 text-sm"
              value={trialScope}
              onChange={(event) => setTrialScope(event.target.value as 'Q1' | 'Q2' | 'BOTH')}
            >
              <option value="Q1">Q1</option>
              <option value="Q2">Q2</option>
              <option value="BOTH">Both</option>
            </select>
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-200">
            Trials:
            <input
              type="number"
              min={1}
              max={50000}
              value={trialCount}
              onChange={(event) => setTrialCount(Number(event.target.value))}
              className="w-28 rounded-md border border-slate-600 bg-slate-800 px-2 py-1 text-sm"
            />
          </label>
          <button
            onClick={runTrials}
            disabled={disabled || loadingTrials}
            className="rounded-lg bg-quantum-accent px-4 py-2 text-sm font-semibold text-slate-900 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loadingTrials ? 'Running…' : 'Run Trials'}
          </button>
        </div>
        {trialsResult && (
          <div className="grid gap-2 text-sm text-slate-200 md:grid-cols-2">
            <div>
              <h4 className="text-xs uppercase tracking-wide text-slate-400">Counts</h4>
              <pre className="rounded-lg bg-slate-900/80 p-3 text-quantum-accent">{JSON.stringify(trialsResult.counts, null, 2)}</pre>
            </div>
            <div>
              <h4 className="text-xs uppercase tracking-wide text-slate-400">Frequencies</h4>
              <pre className="rounded-lg bg-slate-900/80 p-3 text-quantum-accent">{JSON.stringify(trialsResult.freqs, null, 2)}</pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ControlBar;
