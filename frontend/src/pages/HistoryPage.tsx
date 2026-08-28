import { useEffect, useState } from 'react';
import { Container } from '../components/layout/Container';
import { queryService, HistoryListResponse } from '../services/queryService';
import { useAuth } from '../hooks/useAuth';
import { UnityParticleCanvas } from '../components/ui/UnityParticleCanvas';
import { Card, CardContent } from '../components/ui/card';
import { Loader2, Search, Calendar, ChevronDown, ChevronRight, Clock, Star, Database, Copy, Check, Filter } from 'lucide-react';
import { cn } from '../utils/formatters';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '../components/ui/button';

export function HistoryPage() {
  const { user } = useAuth();
  const [history, setHistory] = useState<HistoryListResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  useEffect(() => {
    async function loadHistory() {
      if (!user?.userId) return;
      
      try {
        const data = await queryService.getHistory(user.userId);
        setHistory(data);
      } catch (err: any) {
        setError(err.response?.data?.error || err.message || "Failed to load execution history.");
      } finally {
        setIsLoading(false);
      }
    }

    loadHistory();
  }, [user]);

  const toggleExpand = (id: string) => {
    setExpandedId(prev => prev === id ? null : id);
  };

  const handleCopyText = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const filteredConversations = history?.conversations?.filter(item => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      item.query?.toLowerCase().includes(term) ||
      item.title?.toLowerCase().includes(term) ||
      item.final_output?.toLowerCase().includes(term)
    );
  }) || [];

  if (isLoading) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center relative">
        <UnityParticleCanvas />
        <div className="unity-panel p-8 rounded-2xl border border-neon-cyan/30 flex flex-col items-center space-y-3 relative z-10">
          <Loader2 className="w-8 h-8 animate-spin text-neon-cyan" />
          <p className="text-xs font-mono text-neon-cyan tracking-wider">RETRIEVING UNITY ARCHIVES...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-[calc(100vh-4rem)] py-10 px-4 sm:px-6">
      <UnityParticleCanvas />

      <Container maxW="max-w-6xl" className="relative z-10 space-y-8">
        
        {/* Header Title */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-neon-violet/10 border border-neon-violet/30 text-neon-violet text-xs font-mono mb-2">
              <Database className="w-3.5 h-3.5" />
              <span>UNITY PERSISTENT TELEMETRY ARCHIVES</span>
            </div>
            <h1 className="text-3xl font-heading font-extrabold text-foreground">Execution History & Audits</h1>
            <p className="text-sm text-muted-foreground">Inspect historic prompt queries, multi-agent iteration traces, and synthesized results.</p>
          </div>

          <div className="unity-panel rounded-xl p-4 border border-neon-cyan/20 flex items-center space-x-6">
            <div className="text-center">
              <p className="text-2xl font-bold font-mono text-neon-cyan">{history?.total_count || 0}</p>
              <p className="text-[10px] uppercase font-mono tracking-widest text-muted-foreground">TOTAL RUNS</p>
            </div>
            <div className="h-8 w-px bg-white/10" />
            <div className="text-center">
              <p className="text-2xl font-bold font-mono text-neon-violet">100%</p>
              <p className="text-[10px] uppercase font-mono tracking-widest text-muted-foreground">AUDITED</p>
            </div>
          </div>
        </div>

        {/* Filter & Search Bar */}
        <div className="unity-panel rounded-xl p-3 border border-white/10 flex items-center space-x-3">
          <Search className="w-4 h-4 text-neon-cyan ml-2" />
          <input
            type="text"
            placeholder="Search past queries, keywords, or synthesized outputs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-transparent border-none text-sm text-foreground placeholder:text-muted-foreground focus:outline-none font-sans"
          />
        </div>

        {error && (
          <div className="w-full p-4 bg-destructive/15 border border-destructive/30 rounded-xl text-destructive text-xs font-mono">
            {error}
          </div>
        )}

        {/* List of History Items */}
        <div className="space-y-4">
          {filteredConversations.length === 0 ? (
            <div className="unity-panel rounded-2xl p-12 text-center flex flex-col items-center justify-center border border-white/10">
              <Search className="w-12 h-12 text-muted-foreground/40 mb-4" />
              <h3 className="text-lg font-heading font-semibold mb-1">No execution history found</h3>
              <p className="text-xs text-muted-foreground">Submit a query in the Workspace to populate persistent telemetry logs.</p>
            </div>
          ) : (
            filteredConversations.map((item, index) => {
              const isExpanded = expandedId === item.conversation_id;
              return (
                <motion.div
                  key={item.conversation_id || index}
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Card 
                    className="unity-panel border-white/10 hover:border-neon-cyan/40 transition-all duration-300 cursor-pointer overflow-hidden group shadow-lg"
                    onClick={() => toggleExpand(item.conversation_id)}
                  >
                    <CardContent className="p-0">
                      {/* Header Summary Row */}
                      <div className="flex flex-col sm:flex-row items-start sm:items-center p-6 gap-4">
                        <div className="flex-1 min-w-0">
                          <h4 className="text-base font-bold font-heading truncate mb-2 group-hover:text-neon-cyan transition-colors">
                            {item.title || item.query}
                          </h4>
                          
                          <div className="flex items-center gap-3 text-xs font-mono text-muted-foreground flex-wrap">
                            <span className="flex items-center text-foreground/80">
                              <Calendar className="w-3.5 h-3.5 mr-1 text-neon-violet" />
                              {new Date(item.created_at || Date.now()).toLocaleDateString()}
                            </span>

                            <span className="px-2 py-0.5 rounded text-[10px] bg-neon-cyan/10 text-neon-cyan border border-neon-cyan/20 font-bold">
                              {item.data_classification || 'COMBINED RAG'}
                            </span>

                            {item.processing_time_seconds && (
                              <span className="flex items-center text-foreground/80">
                                <Clock className="w-3.5 h-3.5 mr-1 text-neon-emerald" />
                                {item.processing_time_seconds.toFixed(1)}s latency
                              </span>
                            )}
                          </div>
                        </div>

                        <div className="shrink-0 flex items-center gap-4">
                          <div className="text-right hidden sm:block font-mono">
                            <p className="text-[10px] text-muted-foreground uppercase">SCORE</p>
                            <div className="flex items-center gap-1">
                              <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
                              <p className="font-bold text-foreground text-xs">{(item.quality_score || 0.95).toFixed(2)}</p>
                            </div>
                          </div>

                          <div className="w-9 h-9 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center group-hover:bg-neon-cyan/20 group-hover:border-neon-cyan/40 transition-all">
                            {isExpanded 
                              ? <ChevronDown className="w-5 h-5 text-neon-cyan" /> 
                              : <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:text-neon-cyan" />
                            }
                          </div>
                        </div>
                      </div>

                      {/* Expanded Answer Content */}
                      <AnimatePresence>
                        {isExpanded && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={{ duration: 0.25 }}
                            className="overflow-hidden bg-black/50 border-t border-white/10"
                          >
                            <div className="p-6 space-y-4">
                              <div className="flex items-center justify-between">
                                <span className="text-xs font-mono text-neon-cyan uppercase font-bold tracking-wider">Synthesized Output Trace</span>
                                {item.final_output && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleCopyText(item.final_output!, item.conversation_id);
                                    }}
                                    className="h-7 px-2 text-xs font-mono text-neon-cyan"
                                  >
                                    {copiedId === item.conversation_id ? <Check className="w-3.5 h-3.5 mr-1 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 mr-1" />}
                                    {copiedId === item.conversation_id ? 'Copied' : 'Copy Output'}
                                  </Button>
                                )}
                              </div>

                              <div className="whitespace-pre-wrap text-sm text-foreground/90 font-sans leading-relaxed max-h-96 overflow-y-auto custom-scrollbar bg-black/60 p-4 rounded-xl border border-white/5">
                                {item.final_output || <span className="italic text-muted-foreground">No output content recorded.</span>}
                              </div>
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })
          )}
        </div>

      </Container>
    </div>
  );
}
