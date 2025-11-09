import React from 'react';
import clsx from 'clsx';

type MeasureButtonProps = {
  qubit: 'Q1' | 'Q2' | 'BOTH';
  onMeasure: (scope: 'Q1' | 'Q2' | 'BOTH') => void;
  disabled?: boolean;
};

const MeasureButton: React.FC<MeasureButtonProps> = ({ qubit, onMeasure, disabled }) => {
  return (
    <button
      type="button"
      className={clsx(
        'rounded-full bg-quantum-accent px-4 py-2 text-sm font-semibold text-slate-900 shadow-lg transition hover:brightness-110 focus:outline-none focus:ring-2 focus:ring-quantum-accent/80',
        disabled && 'cursor-not-allowed opacity-60'
      )}
      aria-label={`Measure ${qubit}`}
      disabled={disabled}
      onClick={() => onMeasure(qubit)}
    >
      Measure {qubit}
    </button>
  );
};

export default MeasureButton;
