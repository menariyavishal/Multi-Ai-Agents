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
  isSelected?: boolean;
  onSelect?: (id: string) => void;
}

export function AgentNode({ id, name, icon, state, index, isSelected, onSelect }: AgentNodeProps) {
  const getColors = () => {
    switch (state) {
      case 'processing':
        return 'border-neon-cyan bg-neon-cyan/15 text-neon-cyan ring-4 ring-neon-cyan/25 shadow-lg shadow-neon-cyan/30';
      case 'completed':
        return 'border-neon-violet bg-neon-violet/20 text-neon-violet shadow-lg shadow-neon-violet/20';
      case 'error':
        return 'border-destructive bg-destructive/15 text-destructive shadow-lg shadow-destructive/30';
      case 'pending':
      default:
        return 'border-white/10 bg-black/40 text-muted-foreground opacity-60 hover:opacity-100 hover:border-white/20';
    }
  };

  const getStatusBadge = () => {
    switch (state) {
      case 'processing': return <span className="text-[10px] font-mono text-neon-cyan uppercase font-bold tracking-wider animate-pulse">EXECUTING</span>;
      case 'completed': return <span className="text-[10px] font-mono text-emerald-400 uppercase font-bold tracking-wider">VERIFIED</span>;
      case 'error': return <span className="text-[10px] font-mono text-destructive uppercase font-bold tracking-wider">ERROR</span>;
      default: return <span className="text-[10px] font-mono text-muted-foreground uppercase tracking-wider">STANDBY</span>;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 25, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ delay: index * 0.08, duration: 0.4, type: 'spring' }}
      whileHover={{ scale: 1.05, y: -4 }}
      whileTap={{ scale: 0.96 }}
      onClick={() => onSelect?.(id)}
      className="flex flex-col items-center group relative z-10 cursor-pointer select-none"
    >
      {/* Unity Node Card Container */}
      <div 
        className={cn(
          "relative flex flex-col items-center justify-center p-3 rounded-2xl border-2 backdrop-blur-xl transition-all duration-300 min-w-[90px]",
          getColors(),
          isSelected && "ring-4 ring-neon-cyan/50 border-neon-cyan"
        )}
      >
        {/* Input Execution Socket Dot */}
        <div className="absolute -left-2 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-black border-2 border-neon-cyan shadow-sm" />
        
        {/* Output Execution Socket Dot */}
        <div className="absolute -right-2 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-black border-2 border-neon-violet shadow-sm" />

        {/* Glow ambient highlight */}
        {state === 'processing' && (
          <div className="absolute inset-0 -z-10 rounded-2xl bg-neon-cyan opacity-30 blur-xl animate-pulse" />
        )}

        {/* Node Icon */}
        <div className="z-10 h-7 w-7 mb-1.5 flex items-center justify-center">
          {icon}
        </div>

        {/* Node Name */}
        <p className={cn(
          "text-xs font-bold font-heading tracking-wide transition-colors duration-300 text-center", 
          state === 'processing' ? 'text-neon-cyan' : 
          state === 'completed' ? 'text-foreground' : 'text-muted-foreground'
        )}>
          {name}
        </p>

        {/* State Tag */}
        <div className="mt-1">
          {getStatusBadge()}
        </div>
      </div>
    </motion.div>
  );
}
