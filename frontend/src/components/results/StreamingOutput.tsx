import { StreamEvent } from '../../hooks/useAgentStream';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal } from 'lucide-react';
import { useEffect, useRef } from 'react';

interface StreamingOutputProps {
  events: StreamEvent[];
  isStreaming: boolean;
}

export function StreamingOutput({ events, isStreaming }: StreamingOutputProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events]);

  if (events.length === 0 && !isStreaming) return null;

  return (
    <div className="rounded-xl overflow-hidden glass-panel border-glass-border">
      <div className="bg-black/60 px-4 py-2 border-b border-glass-border flex items-center">
        <Terminal className="w-4 h-4 mr-2 text-brand-cyan" />
        <span className="text-xs font-mono text-muted-foreground uppercase tracking-wider">Activity Log</span>
      </div>
      
      <div 
        ref={scrollRef}
        className="p-4 bg-black/40 h-[200px] overflow-y-auto font-mono text-sm hide-scrollbar"
      >
        <AnimatePresence initial={false}>
          {events.map((event, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="mb-2 text-muted-foreground"
            >
              <div className="flex">
                <span className="text-brand-violet mr-2">[{new Date().toLocaleTimeString(undefined, {hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit'})}]</span>
                <span className="text-brand-cyan mr-2 font-semibold">[{event.node || 'system'}]:</span>
                <span className="text-foreground/80 break-words flex-1">
                  {event.message || `Processed update from agent.`}
                </span>
              </div>
            </motion.div>
          ))}
          {isStreaming && (
            <motion.div 
               initial={{ opacity: 0 }}
               animate={{ opacity: 1 }}
               className="flex items-center text-muted-foreground mt-4 ml-6"
            >
               <span className="animate-pulse">_ waiting for response...</span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
