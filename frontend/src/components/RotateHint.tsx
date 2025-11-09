import React from 'react';

const RotateHint: React.FC = () => {
  return (
    <div className="pointer-events-none fixed inset-0 z-50 flex items-center justify-center bg-slate-900/80 text-center text-slate-100 md:hidden">
      <div className="max-w-xs rounded-2xl border border-slate-700 bg-slate-800/80 p-6 shadow-2xl">
        <p className="text-lg font-semibold">Rotate for the full circuit</p>
        <p className="mt-2 text-sm text-slate-300">
          This experience is optimized for landscape mode. Please rotate your device to explore the two-qubit circuit.
        </p>
      </div>
    </div>
  );
};

export default RotateHint;
