import { Container } from './Container';
import { Cpu, ShieldCheck, Sparkles, Terminal } from 'lucide-react';

export function Footer() {
  return (
    <footer className="border-t border-neon-cyan/15 bg-black/60 py-6 text-xs font-mono text-muted-foreground z-10 relative">
      <Container maxW="max-w-7xl">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          
          <div className="flex items-center space-x-2">
            <Terminal className="w-4 h-4 text-neon-cyan" />
            <span>NEURO-AGENTS ORCHESTRATOR ENGINE v2.5</span>
            <span className="text-white/20">|</span>
            <span className="text-emerald-400 font-semibold">ALL SYSTEMS NOMINAL</span>
          </div>

          <div className="flex items-center space-x-4 flex-wrap justify-center">
            <span className="flex items-center text-neon-violet bg-white/5 border border-white/10 px-2 py-0.5 rounded">
              <Cpu className="w-3 h-3 mr-1" /> Gemini 3.6 Flash
            </span>
            <span className="flex items-center text-neon-cyan bg-white/5 border border-white/10 px-2 py-0.5 rounded">
              <Sparkles className="w-3 h-3 mr-1" /> Groq Llama3 70B
            </span>
            <span className="flex items-center text-neon-emerald bg-white/5 border border-white/10 px-2 py-0.5 rounded">
              <ShieldCheck className="w-3 h-3 mr-1" /> ChromaDB RAG
            </span>
          </div>

        </div>
      </Container>
    </footer>
  );
}
