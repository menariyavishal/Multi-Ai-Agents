import { useState } from 'react';
import { Container } from '../components/layout/Container';
import { QueryForm } from '../components/forms/QueryForm';
import { AgentPipeline } from '../components/agents/AgentPipeline';
import { AgentStatus } from '../components/agents/AgentStatus';
import { useQuery } from '../hooks/useQuery';
import { motion, AnimatePresence } from 'framer-motion';

export function HomePage() {
  const { isLoading, error, sessionId, result, submitQuery, clearQuery } = useQuery();

  const handleQuerySubmit = async (query: string) => {
    clearQuery();
    await submitQuery(query);
  };

  // The backend /query endpoint is synchronous — it returns the full result in one shot.
  // Once result is set, all agents are complete. We don't use SSE streaming here.
  const hasResult = !!result;

  return (
    <Container className="py-10 min-h-[calc(100vh-8rem)]">
      <div className="flex flex-col items-center justify-center space-y-12 max-w-4xl mx-auto w-full">
        
        {/* Header Section */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl md:text-5xl font-heading font-bold bg-gradient-to-r from-brand-violet via-brand-cyan to-white bg-clip-text text-transparent">
            Agentic AI Workspace
          </h1>
          <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
            Harness the power of a 5-agent orchestrator. Ask anything, and watch the planner, researcher, analyst, writer, and reviewer craft your answer.
          </p>
        </div>

        {/* Input Section */}
        <div className="w-full max-w-2xl mx-auto">
          <QueryForm onSubmit={handleQuerySubmit} isLoading={isLoading} />
        </div>

        {error && (
          <div className="w-full max-w-2xl mx-auto p-4 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive text-sm">
            {error}
          </div>
        )}

        {/* Pipeline & Results Section */}
        <AnimatePresence mode="wait">
          {(isLoading || hasResult) && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="w-full space-y-8"
            >
              <div className="glass-panel rounded-2xl p-6 md:p-8 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4">
                  {isLoading && (
                    <div className="animate-pulse flex items-center">
                      <div className="h-2 w-2 rounded-full bg-brand-cyan mr-2"></div>
                      <span className="text-xs text-brand-cyan uppercase tracking-wider font-semibold">Processing</span>
                    </div>
                  )}
                  {hasResult && !isLoading && (
                    <div className="flex items-center">
                      <div className="h-2 w-2 rounded-full bg-emerald-400 mr-2"></div>
                      <span className="text-xs text-emerald-400 uppercase tracking-wider font-semibold">Complete</span>
                    </div>
                  )}
                </div>
                
                <h3 className="text-xl font-heading font-semibold mb-6">Orchestration Pipeline</h3>
                <AgentPipeline graphState={result} activeStreamNode={null} />
                
                <div className="mt-8 pt-6 border-t border-glass-border">
                  <AgentStatus state={result} />
                </div>
              </div>

              {/* Final Result display */}
              {hasResult && result.final_answer && (
                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="glass-panel rounded-2xl p-6 md:p-8"
                >
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-xl font-heading font-semibold text-brand-violet">Final Answer</h3>
                    {result.status === 'needs_revision' && (
                      <span className="text-xs bg-amber-500/20 text-amber-400 border border-amber-500/30 px-3 py-1 rounded-full">
                        Best draft after {result.iterations_used || 3} iterations
                      </span>
                    )}
                  </div>
                  <div className="prose prose-invert max-w-none">
                    <div className="whitespace-pre-wrap text-muted-foreground leading-relaxed">
                      {result.final_answer}
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

      </div>
    </Container>
  );
}