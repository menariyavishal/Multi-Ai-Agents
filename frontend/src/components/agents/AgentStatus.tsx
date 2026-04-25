import { GraphState } from '../../types/graphState';
import { BadgeCheck, RotateCw, AlertTriangle } from 'lucide-react';
import { cn } from '../../utils/formatters';

export function AgentStatus({ state }: { state: GraphState | null }) {
  if (!state) return null;

  return (
    <div className="flex flex-wrap gap-4 items-center justify-between bg-glass border border-glass-border p-4 rounded-xl">
      <div className="flex items-center space-x-2">
        <span className="text-sm font-medium text-muted-foreground mr-2">Status:</span>
        <div className={cn(
          "flex items-center px-3 py-1 rounded-full text-xs font-semibold backdrop-blur-md",
          state.status === 'completed' || state.status === 'approved' ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" : 
          state.status === 'needs_revision' ? "bg-amber-500/20 text-amber-400 border border-amber-500/30" :
          state.status === 'failed' ? "bg-red-500/20 text-red-400 border border-red-500/30" :
          "bg-brand-cyan/20 text-brand-cyan border border-brand-cyan/30"
        )}>
          {state.status === 'completed' || state.status === 'approved' ? <BadgeCheck className="w-3 h-3 mr-1" /> : null}
          {state.status === 'needs_revision' || state.status === 'processing' ? <RotateCw className="w-3 h-3 mr-1 animate-spin" /> : null}
          {state.status === 'failed' ? <AlertTriangle className="w-3 h-3 mr-1" /> : null}
          {state.status.toUpperCase().replace('_', ' ')}
        </div>
      </div>
      
      <div className="flex gap-4 text-xs text-muted-foreground">
        <span className="flex items-center bg-black/40 px-2 py-1 rounded-md border border-glass-border">
          Iterations: <strong className="text-white ml-2">{state.iterations_used || 1}</strong>
        </span>
        <span className="flex items-center bg-black/40 px-2 py-1 rounded-md border border-glass-border">
          Time: <strong className="text-white ml-2">{state.execution_time_seconds ? state.execution_time_seconds.toFixed(1) : 0}s</strong>
        </span>
      </div>
    </div>
  );
}
