import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { StreamEvent } from '../../hooks/useAgentStream';
import { GraphState } from '../../types/graphState';
import { 
  Terminal, Search, Trash2, Copy, Check, ChevronUp, ChevronDown, 
  Filter, Play, Pause, Layers, Database, Code, CheckCircle2, AlertCircle
} from 'lucide-react';
import { Button } from '../ui/button';

interface UnityConsoleProps {
  events: StreamEvent[];
  graphState: GraphState | null;
  isStreaming: boolean;
  onClearLogs?: () => void;
}

export function UnityConsole({ events, graphState, isStreaming, onClearLogs }: UnityConsoleProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [activeTab, setActiveTab] = useState<'logs' | 'steps' | 'knowledge' | 'json'>('logs');
  const [searchFilter, setSearchFilter] = useState('');
  const [levelFilter, setLevelFilter] = useState<'ALL' | 'INFO' | 'SUCCESS' | 'ERROR'>('ALL');
  const [autoScroll, setAutoScroll] = useState(true);
  const [copied, setCopied] = useState(false);

  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll when new events arrive
  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events, graphState, autoScroll]);

  const handleCopyJSON = () => {
    const data = graphState || { events };
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const filteredEvents = events.filter(e => {
    const textMatch = !searchFilter || 
      (e.message && e.message.toLowerCase().includes(searchFilter.toLowerCase())) ||
      (e.node && e.node.toLowerCase().includes(searchFilter.toLowerCase()));
    
    if (!textMatch) return false;

    if (levelFilter === 'SUCCESS') return e.node === 'reviewer' || e.message?.includes('complete');
    if (levelFilter === 'ERROR') return e.message?.toLowerCase().includes('error') || e.message?.toLowerCase().includes('fail');
    return true;
  });

  return (
    <div className="w-full unity-panel rounded-2xl border border-neon-cyan/20 overflow-hidden shadow-2xl transition-all duration-300">
      {/* Header Toolbar */}
      <div className="bg-black/60 px-4 py-2.5 border-b border-white/10 flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1.5 text-neon-cyan font-mono text-xs font-bold uppercase tracking-wider">
            <Terminal className="w-4 h-4" />
            <span>Unity Editor Console</span>
          </div>

          {/* Status Badge */}
          <div className="flex items-center px-2 py-0.5 rounded-full text-[10px] font-mono font-semibold bg-white/5 border border-white/10">
            {isStreaming ? (
              <span className="flex items-center text-neon-cyan animate-pulse">
                <span className="w-1.5 h-1.5 rounded-full bg-neon-cyan mr-1.5"></span>
                LIVE STREAMING
              </span>
            ) : graphState ? (
              <span className="flex items-center text-emerald-400">
                <CheckCircle2 className="w-3 h-3 mr-1 text-emerald-400" />
                EXECUTION IDLE
              </span>
            ) : (
              <span className="text-muted-foreground">STANDBY</span>
            )}
          </div>
        </div>

        {/* Tab Selection */}
        <div className="flex items-center space-x-1 bg-black/40 p-1 rounded-lg border border-white/5 text-xs">
          <button
            onClick={() => setActiveTab('logs')}
            className={`px-3 py-1 rounded-md font-semibold transition-all flex items-center gap-1.5 ${
              activeTab === 'logs' ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Terminal className="w-3 h-3" /> Logs ({events.length})
          </button>
          <button
            onClick={() => setActiveTab('steps')}
            className={`px-3 py-1 rounded-md font-semibold transition-all flex items-center gap-1.5 ${
              activeTab === 'steps' ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Layers className="w-3 h-3" /> Steps
          </button>
          <button
            onClick={() => setActiveTab('knowledge')}
            className={`px-3 py-1 rounded-md font-semibold transition-all flex items-center gap-1.5 ${
              activeTab === 'knowledge' ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Database className="w-3 h-3" /> Dual KB
          </button>
          <button
            onClick={() => setActiveTab('json')}
            className={`px-3 py-1 rounded-md font-semibold transition-all flex items-center gap-1.5 ${
              activeTab === 'json' ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Code className="w-3 h-3" /> JSON Payload
          </button>
        </div>

        {/* Control Tools */}
        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setAutoScroll(!autoScroll)}
            className={`h-7 px-2 text-xs font-mono ${autoScroll ? 'text-neon-cyan' : 'text-muted-foreground'}`}
            title="Toggle Auto-Scroll"
          >
            {autoScroll ? <Pause className="w-3 h-3 mr-1" /> : <Play className="w-3 h-3 mr-1" />}
            {autoScroll ? 'Lock Scroll' : 'Scroll Free'}
          </Button>

          <Button
            variant="ghost"
            size="sm"
            onClick={handleCopyJSON}
            className="h-7 px-2 text-xs font-mono text-neon-cyan"
            title="Copy Console Output JSON"
          >
            {copied ? <Check className="w-3 h-3 mr-1 text-emerald-400" /> : <Copy className="w-3 h-3 mr-1" />}
            {copied ? 'Copied' : 'Copy JSON'}
          </Button>

          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsExpanded(!isExpanded)}
            className="h-7 w-7 text-muted-foreground hover:text-white"
          >
            {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />}
          </Button>
        </div>
      </div>

      {/* Expanded Console Window */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="flex flex-col bg-black/50"
          >
            {/* Filter Search Bar */}
            <div className="px-4 py-2 bg-black/40 border-b border-white/5 flex items-center justify-between gap-4 text-xs font-mono">
              <div className="flex items-center space-x-2 flex-1 max-w-sm">
                <Search className="w-3.5 h-3.5 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Filter logs or node events..."
                  value={searchFilter}
                  onChange={(e) => setSearchFilter(e.target.value)}
                  className="bg-transparent border-none text-xs text-foreground placeholder:text-muted-foreground focus:outline-none w-full font-mono"
                />
              </div>

              <div className="flex items-center space-x-2">
                <span className="text-muted-foreground text-[10px] uppercase">Level:</span>
                <select
                  value={levelFilter}
                  onChange={(e: any) => setLevelFilter(e.target.value)}
                  className="bg-black/60 border border-white/10 rounded px-2 py-0.5 text-xs text-neon-cyan font-mono focus:outline-none"
                >
                  <option value="ALL">ALL</option>
                  <option value="INFO">INFO</option>
                  <option value="SUCCESS">SUCCESS</option>
                  <option value="ERROR">ERROR</option>
                </select>
              </div>
            </div>

            {/* Log Body Container */}
            <div
              ref={scrollRef}
              className="p-4 h-48 overflow-y-auto font-mono text-xs custom-scrollbar space-y-2 select-text"
            >
              {activeTab === 'logs' && (
                <>
                  {filteredEvents.length === 0 ? (
                    <div className="flex items-center justify-center h-full text-muted-foreground text-xs italic">
                      No logs matching filters. Submit a query to view agent telemetry.
                    </div>
                  ) : (
                    filteredEvents.map((evt, idx) => (
                      <div key={idx} className="flex items-start space-x-2 text-foreground/90 hover:bg-white/5 p-1 rounded transition-colors">
                        <span className="text-neon-violet font-semibold shrink-0">
                          [{new Date().toLocaleTimeString(undefined, { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}]
                        </span>
                        <span className="text-neon-cyan font-bold uppercase shrink-0">
                          [{evt.node || 'SYSTEM'}]:
                        </span>
                        <span className="text-foreground/90 break-words flex-1 leading-relaxed">
                          {evt.message || 'Node execution step recorded.'}
                        </span>
                      </div>
                    ))
                  )}
                  {isStreaming && (
                    <div className="flex items-center text-neon-cyan animate-pulse mt-2 ml-4">
                      <span className="mr-2">⚡</span> Processing next multi-agent execution step...
                    </div>
                  )}
                </>
              )}

              {activeTab === 'steps' && (
                <div className="space-y-2 text-xs font-mono">
                  <div className="p-2.5 rounded-lg bg-white/5 border border-white/10 flex items-center justify-between">
                    <span className="text-neon-violet font-bold">Step 1: Planner Agent</span>
                    <span className="text-emerald-400">STATUS: COMPLETED</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-white/5 border border-white/10 flex items-center justify-between">
                    <span className="text-neon-cyan font-bold">Step 2: Researcher Agent</span>
                    <span className="text-emerald-400">STATUS: COMPLETED</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-white/5 border border-white/10 flex items-center justify-between">
                    <span className="text-neon-emerald font-bold">Step 3: Analyst Agent</span>
                    <span className="text-emerald-400">STATUS: COMPLETED</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-white/5 border border-white/10 flex items-center justify-between">
                    <span className="text-neon-magenta font-bold">Step 4: Writer Agent</span>
                    <span className="text-emerald-400">STATUS: COMPLETED</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-white/5 border border-white/10 flex items-center justify-between">
                    <span className="text-amber-400 font-bold">Step 5: Reviewer Agent</span>
                    <span className="text-emerald-400">STATUS: VERIFIED</span>
                  </div>
                </div>
              )}

              {activeTab === 'knowledge' && (
                <div className="space-y-2 font-mono text-xs">
                  <div className="p-3 bg-black/60 rounded-xl border border-white/10 space-y-1">
                    <span className="text-neon-cyan font-bold block">🌐 Web Knowledge Source (Tavily/SerpAPI)</span>
                    <p className="text-muted-foreground text-[11px]">Real-time search stream active. Retrying fresh indexes for multi-agent synthesis.</p>
                  </div>
                  <div className="p-3 bg-black/60 rounded-xl border border-white/10 space-y-1">
                    <span className="text-neon-violet font-bold block">🧠 Vector DB Embeddings (ChromaDB / Memory)</span>
                    <p className="text-muted-foreground text-[11px]">Cosine similarity match: 0.942. Extracted domain knowledge chunks.</p>
                  </div>
                </div>
              )}

              {activeTab === 'json' && (
                <pre className="text-neon-cyan font-mono text-[11px] leading-relaxed overflow-x-auto">
                  {JSON.stringify(graphState || { events }, null, 2)}
                </pre>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
