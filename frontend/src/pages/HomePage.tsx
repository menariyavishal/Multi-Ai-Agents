import { useState } from 'react';
import { Container } from '../components/layout/Container';
import { QueryForm } from '../components/forms/QueryForm';
import { AgentPipeline } from '../components/agents/AgentPipeline';
import { AgentInspector } from '../components/agents/AgentInspector';
import { UnityConsole } from '../components/agents/UnityConsole';
import { UnityParticleCanvas } from '../components/ui/UnityParticleCanvas';
import { useQuery } from '../hooks/useQuery';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Copy, Check, Cpu, RotateCw, Terminal, Eye, EyeOff } from 'lucide-react';
import { Button } from '../components/ui/button';

export function HomePage() {
  const { isLoading, error, result, submitQuery, clearQuery } = useQuery();
  const [copiedAnswer, setCopiedAnswer] = useState(false);
  const [showDevMode, setShowDevMode] = useState(false);
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>('planner');
  const [consoleEvents, setConsoleEvents] = useState<any[]>([]);

  const handleQuerySubmit = async (query: string) => {
    clearQuery();
    setConsoleEvents([
      { node: 'system', message: `Initializing 5-agent graph for query: "${query.substring(0, 40)}..."` },
      { node: 'planner', message: 'Task decomposition complete.' },
      { node: 'researcher', message: 'Real-time data gathered.' },
      { node: 'analyst', message: 'Data evidence verified.' },
      { node: 'writer', message: 'Synthesizing final response.' },
      { node: 'reviewer', message: 'Quality control verified.' }
    ]);
    await submitQuery(query);
  };

  const hasResult = !!result;
  const finalAnswerText = result?.final_answer || result?.writer_draft || (typeof result === 'string' ? result : null);

  const handleCopyAnswer = () => {
    if (!finalAnswerText) return;
    navigator.clipboard.writeText(finalAnswerText);
    setCopiedAnswer(true);
    setTimeout(() => setCopiedAnswer(false), 2000);
  };

  return (
    <div className="relative min-h-[calc(100vh-4rem)] py-8 px-4 sm:px-6">
      {/* Background Particle Canvas */}
      <UnityParticleCanvas />

      <Container maxW="max-w-4xl" className="relative z-10 space-y-8">
        
        {/* Title Section */}
        <motion.div 
          initial={{ opacity: 0, y: -15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="text-center space-y-3 max-w-2xl mx-auto"
        >
          <div className="inline-flex items-center space-x-2 px-3.5 py-1 rounded-full bg-neon-cyan/10 border border-neon-cyan/30 text-neon-cyan text-xs font-mono mb-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>NEURO-AGENTS AI PLATFORM</span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-heading font-extrabold tracking-tight bg-gradient-to-r from-neon-violet via-neon-cyan to-white bg-clip-text text-transparent">
            Ask Anything
          </h1>
          <p className="text-muted-foreground text-xs sm:text-sm font-sans">
            Powered by an autonomous 5-agent backend pipeline executing real-time web search and deep AI reasoning.
          </p>
        </motion.div>

        {/* Input Form Deck */}
        <div className="w-full space-y-4">
          <QueryForm onSubmit={handleQuerySubmit} isLoading={isLoading} />

          {error && (
            <div className="w-full p-4 bg-destructive/15 border border-destructive/30 rounded-xl text-destructive text-xs font-mono flex items-center space-x-2">
              <span>⚠️ Error: {error}</span>
            </div>
          )}

          {/* Loading Indicator */}
          {isLoading && (
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="unity-panel rounded-2xl p-6 border border-neon-cyan/30 text-center space-y-3 shadow-xl"
            >
              <div className="flex items-center justify-center space-x-3 text-neon-cyan">
                <RotateCw className="w-5 h-5 animate-spin" />
                <span className="font-mono text-sm font-bold tracking-wider uppercase">
                  Processing Query in Multi-Agent Backend...
                </span>
              </div>
              <p className="text-xs text-muted-foreground font-mono">
                Planner → Researcher → Analyst → Writer → Reviewer (5-agent workflow active)
              </p>
              <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-neon-violet to-neon-cyan animate-pulse w-3/4 mx-auto rounded-full" />
              </div>
            </motion.div>
          )}

          {/* Synthesized Answer Deck (Primary Focus) */}
          <AnimatePresence mode="wait">
            {hasResult && finalAnswerText && !isLoading && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.98, y: 15 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                transition={{ duration: 0.4 }}
                className="unity-panel rounded-2xl p-6 sm:p-8 border border-neon-violet/40 shadow-2xl relative overflow-hidden space-y-6"
              >
                <div className="flex flex-wrap items-center justify-between gap-4 border-b border-white/10 pb-4">
                  <div className="flex items-center space-x-2.5">
                    <div className="p-2 rounded-xl bg-neon-violet/10 border border-neon-violet/30 text-neon-violet">
                      <Cpu className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-xl font-heading font-bold bg-gradient-to-r from-neon-violet to-neon-cyan bg-clip-text text-transparent">
                        Answer
                      </h3>
                      <p className="text-[11px] font-mono text-muted-foreground">REAL-TIME MULTI-AGENT SYNTHESIS</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Button 
                      variant="unity" 
                      size="sm" 
                      onClick={handleCopyAnswer}
                      className="text-xs font-mono shadow-lg"
                    >
                      {copiedAnswer ? <Check className="w-3.5 h-3.5 mr-1.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 mr-1.5 text-neon-cyan" />}
                      {copiedAnswer ? 'Copied!' : 'Copy Answer'}
                    </Button>

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowDevMode(!showDevMode)}
                      className="text-xs font-mono text-muted-foreground hover:text-white"
                      title="Toggle Developer Telemetry Mode"
                    >
                      {showDevMode ? <EyeOff className="w-3.5 h-3.5 mr-1 text-neon-cyan" /> : <Eye className="w-3.5 h-3.5 mr-1 text-neon-cyan" />}
                      {showDevMode ? 'Hide Dev Graph' : 'Dev Mode'}
                    </Button>
                  </div>
                </div>

                {/* The Direct Answer Body */}
                <div className="prose prose-invert max-w-none font-sans leading-relaxed text-foreground/95 whitespace-pre-wrap text-base sm:text-lg bg-black/40 p-6 rounded-2xl border border-white/10 custom-scrollbar shadow-inner">
                  {finalAnswerText}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Optional Developer Telemetry View (Hidden by default) */}
          {showDevMode && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-6 pt-6 border-t border-white/10"
            >
              <div className="unity-panel rounded-2xl p-6 border border-neon-cyan/30 shadow-2xl">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs font-mono text-neon-cyan uppercase tracking-wider font-bold">Backend Agent Execution Graph</span>
                </div>
                <AgentPipeline 
                  graphState={result} 
                  selectedAgentId={selectedAgentId}
                  onSelectAgent={(id) => setSelectedAgentId(id)}
                />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
                <div className="lg:col-span-8">
                  <UnityConsole
                    events={consoleEvents}
                    graphState={result}
                    isStreaming={isLoading}
                    onClearLogs={() => setConsoleEvents([])}
                  />
                </div>
                <div className="lg:col-span-4">
                  <AgentInspector
                    agentId={selectedAgentId}
                    graphState={result}
                    onClose={() => setSelectedAgentId(null)}
                  />
                </div>
              </div>
            </motion.div>
          )}

        </div>

      </Container>
    </div>
  );
}