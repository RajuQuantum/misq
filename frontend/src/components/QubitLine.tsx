import React from 'react';
import MeasureButton from './MeasureButton';
import LED from './LED';
import type { QubitId } from '../types';

interface QubitLineProps {
  qubit: QubitId;
  gates?: React.ReactNode;
  ledValue: 0 | 1;
  blinking: boolean;
  onMeasure: (scope: QubitId) => void;
  disabled?: boolean;
}

const QubitLine: React.FC<QubitLineProps> = ({ qubit, gates, ledValue, blinking, onMeasure, disabled }) => {
  return (
    <div className="flex w-full items-center gap-4">
      <div className="flex h-32 w-full items-center justify-between rounded-2xl border border-slate-700 bg-slate-900/40 px-6 py-4">
        <div className="flex h-full flex-1 items-center justify-start gap-6">
          <div className="flex h-2 flex-1 items-center rounded-full bg-slate-700">
            <div className="flex w-full items-center justify-center gap-6">
              {gates}
            </div>
          </div>
        </div>
        <div className="flex flex-col items-center gap-3">
          <MeasureButton qubit={qubit} onMeasure={onMeasure} disabled={disabled} />
          <span className="text-xs uppercase tracking-wide text-slate-400">Measure {qubit}</span>
        </div>
      </div>
      <div className="flex flex-col items-center gap-2">
        <LED qubit={qubit} value={ledValue} blinking={blinking} />
        <span className="text-xs font-semibold text-slate-300">{qubit}</span>
      </div>
    </div>
  );
};

export default QubitLine;
