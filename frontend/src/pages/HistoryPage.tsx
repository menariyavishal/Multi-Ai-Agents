import { useEffect, useState } from 'react';
import { Container } from '../components/layout/Container';
import { queryService, HistoryListResponse } from '../services/queryService';
import { useAuth } from '../hooks/useAuth';
import { Card, CardContent } from '../components/ui/card';
import { Loader2, Search, Calendar, ChevronDown, ChevronRight, Clock, Star } from 'lucide-react';
import { cn } from '../utils/formatters';
import { motion, AnimatePresence } from 'framer-motion';

export function HistoryPage() {
  const { user } = useAuth();
  const [history, setHistory] = useState<HistoryListResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    async function loadHistory() {
      if (!user?.userId) return;
      
      try {
        const data = await queryService.getHistory(user.userId);
        setHistory(data);
      } catch (err: any) {
        setError(err.response?.data?.error || err.message || "Failed to load history");
      } finally {
        setIsLoading(false);
      }
    }

    loadHistory();
  }, [user]);

  const toggleExpand = (id: string) => {
    setExpandedId(prev => prev === id ? null : id);
  };

  if (isLoading) {
    return (
      <Container className="py-20 flex justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-brand-cyan" />
      </Container>
    );
  }

  return (
    <Container className="py-10">
      <div className="flex flex-col space-y-8 max-w-4xl mx-auto">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-heading font-bold mb-2">Conversation History</h1>
            <p className="text-muted-foreground">View your past queries and agent outputs.</p>
          </div>
          <div className="bg-glass border border-glass-border rounded-lg p-3 flex items-center space-x-4">
             <div className="text-center">
                <p className="text-2xl font-bold font-heading text-brand-cyan">{history?.total_count || 0}</p>
                <p className="text-xs uppercase tracking-wider text-muted-foreground font-semibold">Queries</p>
             </div>
          </div>
        </div>

        {error && (
          <div className="w-full p-4 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive text-sm">
            {error}
          </div>
        )}

        <div className="space-y-4">
          {!history?.conversations || history.conversations.length === 0 ? (
            <div className="glass-panel rounded-xl p-12 text-center flex flex-col items-center justify-center">
              <Search className="w-12 h-12 text-muted-foreground mb-4 opacity-50" />
              <h3 className="text-xl font-heading font-semibold mb-2">No history found</h3>
              <p className="text-muted-foreground">You haven't asked the agents any queries yet.</p>
            </div>
          ) : (
            history.conversations.map((item, index) => {
              const isExpanded = expandedId === item.conversation_id;
              return (
                <Card 
                  key={item.conversation_id || index} 
                  className="border-glass-border hover:border-brand-violet/50 transition-colors cursor-pointer group glass-panel"
                  onClick={() => toggleExpand(item.conversation_id)}
                >
                  <CardContent className="p-0">
                    {/* Header Row */}
                    <div className="flex items-start md:items-center p-6 flex-col md:flex-row gap-4">
                      <div className="flex-1 min-w-0">
                          <h4 className="text-lg font-medium truncate mb-2 group-hover:text-brand-cyan transition-colors">
                             {item.title || item.query}
                          </h4>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground flex-wrap">
                              <span className="flex items-center">
                                <Calendar className="w-3 h-3 mr-1" />
                                {new Date(item.created_at || Date.now()).toLocaleDateString()}
                              </span>
                              <span className={cn(
                                "px-2 py-0.5 rounded-full border",
                                "bg-glass-border border-white/10"
                              )}>
                                {item.data_classification || 'COMBINED'}
                              </span>
                              {item.processing_time_seconds && (
                                <span className="flex items-center">
                                  <Clock className="w-3 h-3 mr-1" />
                                  {item.processing_time_seconds.toFixed(1)}s
                                </span>
                              )}
                          </div>
                      </div>
                      <div className="shrink-0 flex items-center gap-6">
                          <div className="text-right hidden sm:block">
                              <p className="text-xs text-muted-foreground">Quality</p>
                              <div className="flex items-center gap-1">
                                  <Star className="w-3 h-3 text-amber-400" />
                                  <p className="font-semibold text-foreground">{(item.quality_score || 0).toFixed(2)}</p>
                              </div>
                          </div>
                          <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center group-hover:bg-brand-violet/20 transition-colors">
                              {isExpanded 
                                ? <ChevronDown className="w-5 h-5 text-brand-violet" /> 
                                : <ChevronRight className="w-5 h-5 text-muted-foreground group-hover:text-brand-violet" />
                              }
                          </div>
                      </div>
                    </div>

                    {/* Expanded Output */}
                    <AnimatePresence>
                      {isExpanded && item.final_output && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.2 }}
                          className="overflow-hidden"
                        >
                          <div className="px-6 pb-6 pt-2 border-t border-glass-border">
                            <h5 className="text-sm font-semibold text-brand-violet mb-3 uppercase tracking-wider">Agent Output</h5>
                            <div className="whitespace-pre-wrap text-sm text-muted-foreground leading-relaxed max-h-96 overflow-y-auto pr-2">
                              {item.final_output}
                            </div>
                          </div>
                        </motion.div>
                      )}

                      {isExpanded && !item.final_output && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          className="overflow-hidden"
                        >
                          <div className="px-6 pb-6 pt-2 border-t border-glass-border">
                            <p className="text-sm text-muted-foreground italic">No output stored for this conversation.</p>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </CardContent>
                </Card>
              );
            })
          )}
        </div>
      </div>
    </Container>
  );
}
