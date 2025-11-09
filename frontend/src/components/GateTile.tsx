import { motion } from 'framer-motion';
import { GateType } from '../types';
import clsx from 'clsx';
import React from 'react';

type GateTileProps = {
  gate: GateType;
  label: string;
  description: string;
  active: boolean;
  disabled?: boolean;
  onClick: (gate: GateType) => void;
};

const GateTile: React.FC<GateTileProps> = ({ gate, label, description, active, disabled, onClick }) => {
  return (
    <motion.button
      layout
      disabled={disabled}
      aria-pressed={active}
      aria-label={`Apply gate ${label}`}
      onClick={() => onClick(gate)}
      whileTap={{ scale: disabled ? 1 : 0.96 }}
      className={clsx(
        'relative flex h-24 w-28 flex-col items-center justify-center rounded-xl border border-slate-700 bg-quantum-panel text-center text-lg font-semibold text-slate-100 shadow-lg transition-all',
        disabled && 'cursor-not-allowed opacity-60',
        active && 'animate-pulseAura border-quantum-accent'
      )}
    >
      <span className="text-xs uppercase tracking-wide text-slate-300">{label}</span>
      <span className="text-2xl font-bold">{gate}</span>
      <span className="mt-1 text-[11px] text-slate-400">{description}</span>
      {active && (
        <motion.span
          layoutId={`aura-${gate}`}
          className="pointer-events-none absolute inset-0 rounded-xl ring-4 ring-quantum-accent/40"
          animate={{ opacity: [0.4, 0.8, 0.4] }}
          transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
        />
      )}
    </motion.button>
  );
};

export default GateTile;
