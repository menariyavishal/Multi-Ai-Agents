import { motion } from 'framer-motion';
import { ReactNode } from 'react';
import { cn } from '../../utils/formatters';

export type AgentState = 'pending' | 'processing' | 'completed' | 'error';

interface AgentNodeProps {
  id: string;
  name: string;
  icon: ReactNode;
  state: AgentState;
  index: number;
}

export function AgentNode({ name, icon, state, index }: AgentNodeProps) {
  const getColors = () => {
    switch (state) {
      case 'processing':
        return 'border-brand-cyan bg-brand-cyan/10 text-brand-cyan ring-4 ring-brand-cyan/20';
      case 'completed':
        return 'border-brand-violet bg-brand-violet/20 text-foreground';
      case 'error':
        return 'border-destructive bg-destructive/10 text-destructive';
      case 'pending':
      default:
        return 'border-glass-border bg-glass/50 text-muted-foreground opacity-60';
    }
  };

  const isPulsing = state === 'processing';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.4 }}
      className="flex flex-col items-center group relative z-10"
    >
      <div 
        className={cn(
          "relative flex h-16 w-16 items-center justify-center rounded-2xl border-2 backdrop-blur-sm transition-all duration-500",
          getColors(),
          isPulsing && "animate-pulse-glow"
        )}
      >
        {/* Glow effect matching border color but softer */}
        {isPulsing && (
          <div className="absolute inset-0 -z-10 rounded-2xl bg-brand-cyan opacity-20 blur-xl" />
        )}
        <div className="z-10 h-8 w-8">
          {icon}
        </div>
      </div>
      
      <div className="mt-3 text-center">
        <p className={cn(
          "text-sm font-semibold transition-colors duration-300", 
          state === 'processing' ? 'text-brand-cyan font-bold' : 
          state === 'pending' ? 'text-muted-foreground' : 'text-foreground'
        )}>
          {name}
        </p>
      </div>
    </motion.div>
  );
}
