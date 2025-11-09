import { motion } from 'framer-motion';
import clsx from 'clsx';
import React from 'react';

type LEDProps = {
  qubit: 'Q1' | 'Q2';
  value: 0 | 1;
  blinking: boolean;
};

const LED: React.FC<LEDProps> = ({ qubit, value, blinking }) => {
  const color = value === 0 ? 'bg-quantum-green' : 'bg-quantum-red';
  const label = `${qubit} LED indicates state ${value}`;

  return (
    <motion.div
      role="status"
      aria-live="polite"
      aria-label={label}
      className={clsx(
        'flex h-14 w-14 items-center justify-center rounded-full border-4 border-slate-800 shadow-inner transition-all',
        blinking ? 'animate-blink' : '',
        value === 0 ? 'border-quantum-green/60' : 'border-quantum-red/60'
      )}
    >
      <span className={clsx('h-8 w-8 rounded-full shadow-lg', color)} />
    </motion.div>
  );
};

export default LED;
