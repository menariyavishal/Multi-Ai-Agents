import { useState } from 'react';
import { useForm as useHookForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '../ui/button';
import { Send, Loader2, Sparkles, Command, Cpu, ShieldCheck, Zap, BarChart3, Infinity } from 'lucide-react';
import { motion } from 'framer-motion';

const querySchema = z.object({
  query: z.string().min(1, "Please enter a query to process"),
});

type QueryFormData = z.infer<typeof querySchema>;

interface QueryFormProps {
  onSubmit: (query: string) => Promise<void>;
  isLoading: boolean;
}

const PRESET_QUERIES = [
  { label: "🤖 AI Trends 2026", icon: Sparkles, query: "What are the major breakthrough trends in Multi-Agent AI Orchestration for 2026?" },
  { label: "📊 Market Research", icon: BarChart3, query: "Analyze the competitive landscape of cloud data warehouses and AI compute engines." },
  { label: "⚡ Code Architecture", icon: Zap, query: "Design an event-driven high-throughput Microservices architecture using Python and Redis." },
  { label: "🛡️ Security Audit", icon: ShieldCheck, query: "Provide a comprehensive security posture checklist for OAuth2 and JWT authentication systems." },
];

export function QueryForm({ onSubmit, isLoading }: QueryFormProps) {
  const { register, handleSubmit, formState: { errors }, setValue, watch } = useHookForm<QueryFormData>({
    resolver: zodResolver(querySchema),
    defaultValues: { query: '' }
  });

  const queryValue = watch('query');
  const count = queryValue?.length || 0;

  const handleFormSubmit = async (data: QueryFormData) => {
    const text = data.query;
    setValue('query', '', { shouldValidate: false });
    await onSubmit(text);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleSubmit(handleFormSubmit)();
    }
  };

  const selectPreset = (presetQuery: string) => {
    setValue('query', presetQuery, { shouldValidate: true });
  };

  return (
    <div className="w-full unity-panel rounded-2xl p-6 border border-neon-cyan/30 shadow-2xl relative overflow-hidden">
      {/* Top Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 rounded-lg bg-neon-cyan/10 border border-neon-cyan/30 text-neon-cyan">
            <Cpu className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-base font-bold font-heading text-foreground">Orchestrator Command Deck</h2>
            <p className="text-[11px] text-muted-foreground font-mono">UNLIMITED LENGTH QUERY ENGINE</p>
          </div>
        </div>

        <div className="hidden sm:flex items-center space-x-1 text-[11px] text-muted-foreground font-mono bg-black/40 px-2.5 py-1 rounded-md border border-white/5">
          <Command className="w-3 h-3 text-neon-cyan" />
          <span>Press <kbd className="text-neon-cyan font-semibold">Ctrl + Enter</kbd> to execute</span>
        </div>
      </div>

      {/* Preset Chips */}
      <div className="mb-4 flex flex-wrap gap-2">
        {PRESET_QUERIES.map((preset, idx) => {
          const IconComp = preset.icon;
          return (
            <motion.button
              key={idx}
              type="button"
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => selectPreset(preset.query)}
              disabled={isLoading}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-black/50 border border-white/10 hover:border-neon-cyan/50 text-xs text-foreground/80 hover:text-neon-cyan transition-all disabled:opacity-50"
            >
              <IconComp className="w-3.5 h-3.5 text-neon-violet" />
              <span>{preset.label}</span>
            </motion.button>
          );
        })}
      </div>

      {/* Main Textarea Form */}
      <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
        <div className="relative">
          <textarea
            {...register('query')}
            onKeyDown={handleKeyDown}
            rows={4}
            placeholder="Type any query of any length without restriction... (e.g. Detailed research tasks, code snippets, multi-part prompt instructions)"
            disabled={isLoading}
            className="w-full bg-black/60 border border-white/15 rounded-xl p-4 pr-32 text-sm text-foreground placeholder:text-muted-foreground focus:border-neon-cyan focus:ring-2 focus:ring-neon-cyan/20 focus:outline-none transition-all resize-y min-h-[110px] font-sans custom-scrollbar"
          />
          
          {/* Live Character Count Indicator (Unlimited) */}
          <div className="absolute right-3 bottom-4 text-[11px] font-mono text-muted-foreground bg-black/80 px-2.5 py-1 rounded-lg border border-neon-cyan/30 flex items-center space-x-1 shadow-md">
            <span className="text-neon-cyan font-bold">{count}</span>
            <span className="text-muted-foreground text-[10px]">chars</span>
            <span className="text-white/20">|</span>
            <span className="text-emerald-400 font-bold flex items-center gap-0.5">
              <Infinity className="w-3 h-3 text-emerald-400 inline" /> NO LIMIT
            </span>
          </div>
        </div>

        {errors.query && (
          <p className="text-xs text-destructive font-mono">{errors.query.message}</p>
        )}

        <Button 
          type="submit" 
          disabled={isLoading || count < 1} 
          variant="cyber"
          size="lg"
          className="w-full font-mono uppercase tracking-wider font-bold shadow-lg shadow-neon-cyan/20 flex items-center justify-center space-x-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin text-black" />
              <span>Synthesizing Multi-Agent Pipeline...</span>
            </>
          ) : (
            <>
              <Send className="h-4 w-4 text-black" />
              <span>Execute Agentic Pipeline</span>
            </>
          )}
        </Button>
      </form>
    </div>
  );
}
