import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { GraphState } from '../../types/graphState';
import { 
  X, Map, Search, LineChart, PenTool, CheckCircle, 
  Cpu, Database, Sparkles, Sliders, Copy, Check
} from 'lucide-react';
import { Button } from '../ui/button';

interface AgentInspectorProps {
  agentId: string | null;
  graphState: GraphState | null;
  onClose: () => void;
}

const AGENT_DETAILS: Record<string, {
  name: string;
  role: string;
  description: string;
  model: string;
  temperature: number;
  icon: any;
  accent: string;
  tools: string[];
}> = {
  planner: {
    name: "Planner Agent",
    role: "Orchestration & Task Decomposition",
    description: "Breakdowns user intent into structured multi-step execution plans with targeted search subqueries.",
    model: "Gemini 3.6 Flash / Groq Llama3 70B",
    temperature: 0.2,
    icon: Map,
    accent: "border-neon-violet text-neon-violet bg-neon-violet/10",
    tools: ["Query Decomposition", "Sub-task Scheduler", "Dependency Graphing"]
  },
  researcher: {
    name: "Researcher Agent",
    role: "Dual Knowledge Base Retrieval",
    description: "Executes parallel web searches via Tavily/SerpAPI and queries vector databases for ground truth context.",
    model: "Gemini 3.6 Flash / Groq Llama3 70B",
    temperature: 0.3,
    icon: Search,
    accent: "border-neon-cyan text-neon-cyan bg-neon-cyan/10",
    tools: ["Web Search Aggregator", "Vector DB Indexer", "Source Synthesizer"]
  },
  analyst: {
    name: "Analyst Agent",
    role: "Data Processing & Outlier Detection",
    description: "Cross-references findings, detects contradictions, filters noise, and computes evidence confidence scores.",
    model: "Gemini 3.6 Flash / Groq Llama3 70B",
    temperature: 0.1,
    icon: LineChart,
    accent: "border-neon-emerald text-neon-emerald bg-neon-emerald/10",
    tools: ["Fact Verification", "Confidence Scoring", "Gap Analysis"]
  },
  writer: {
    name: "Writer Agent",
    role: "Comprehensive Content Synthesis",
    description: "Drafts publication-ready insights with clear heading structure, detailed evidence, and formatted markdown.",
    model: "Gemini 3.6 Flash / Groq Llama3 70B",
    temperature: 0.4,
    icon: PenTool,
    accent: "border-neon-magenta text-neon-magenta bg-neon-magenta/10",
    tools: ["Markdown Formatter", "Coherence Polisher", "Citation Injector"]
  },
  reviewer: {
    name: "Reviewer Agent",
    role: "Quality Control & Self-Correction",
    description: "Evaluates draft quality against original query constraints. Requests targeted revision loops if criteria fail.",
    model: "Gemini 3.6 Flash / Groq Llama3 70B",
    temperature: 0.1,
    icon: CheckCircle,
    accent: "border-amber-400 text-amber-400 bg-amber-400/10",
    tools: ["Quality Scoring Matrix", "Hallucination Check", "Feedback Router"]
  }
};

export function AgentInspector({ agentId, graphState, onClose }: AgentInspectorProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'output' | 'raw'>('overview');
  const [copied, setCopied] = useState(false);

  if (!agentId) return null;

  const agent = AGENT_DETAILS[agentId] || AGENT_DETAILS.planner;
  const IconComponent = agent.icon;

  const getAgentOutput = (): string => {
    if (!graphState) return 'No execution data available.';
    
    let raw: any = null;
    switch (agentId) {
      case 'planner': raw = graphState.plan; break;
      case 'researcher': raw = graphState.research_summary; break;
      case 'analyst': raw = graphState.analysis; break;
      case 'writer': raw = graphState.draft; break;
      case 'reviewer': raw = graphState.review; break;
    }

    if (!raw) return `${agent.name} is ready for execution.`;
    return typeof raw === 'object' ? JSON.stringify(raw, null, 2) : String(raw);
  };

  const agentOutput = getAgentOutput();

  const handleCopy = () => {
    navigator.clipboard.writeText(agentOutput);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, x: 50, scale: 0.95 }}
        animate={{ opacity: 1, x: 0, scale: 1 }}
        exit={{ opacity: 0, x: 50, scale: 0.95 }}
        transition={{ type: 'spring', stiffness: 300, damping: 25 }}
        className="w-full lg:w-80 shrink-0 unity-panel rounded-2xl p-5 border border-neon-cyan/20 flex flex-col h-full shadow-2xl relative overflow-hidden"
      >
        {/* Top Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/10">
          <div className="flex items-center space-x-2">
            <div className={`p-2 rounded-lg border ${agent.accent}`}>
              <IconComponent className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold font-heading text-foreground uppercase tracking-wider">{agent.name}</h3>
              <p className="text-[11px] text-muted-foreground font-mono">UNITY INSPECTOR</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} className="h-7 w-7 text-muted-foreground hover:text-white">
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Tab Selection */}
        <div className="grid grid-cols-3 gap-1 bg-black/40 p-1 rounded-lg border border-white/5 my-4">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-1.5 text-xs font-semibold rounded-md transition-all ${
              activeTab === 'overview' ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('output')}
            className={`py-1.5 text-xs font-semibold rounded-md transition-all ${
              activeTab === 'output' ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Output
          </button>
          <button
            onClick={() => setActiveTab('raw')}
            className={`py-1.5 text-xs font-semibold rounded-md transition-all ${
              activeTab === 'raw' ? 'bg-neon-cyan/20 text-neon-cyan border border-neon-cyan/30' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Config
          </button>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-y-auto custom-scrollbar space-y-4 pr-1 text-xs">
          {activeTab === 'overview' && (
            <div className="space-y-4">
              <div>
                <span className="text-[10px] text-muted-foreground uppercase font-mono tracking-wider">Role & Purpose</span>
                <p className="mt-1 text-foreground/90 font-medium leading-relaxed">{agent.role}</p>
                <p className="mt-1 text-muted-foreground text-[11px] leading-normal">{agent.description}</p>
              </div>

              <div className="bg-black/30 p-3 rounded-xl border border-white/5 space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground flex items-center gap-1.5">
                    <Cpu className="w-3.5 h-3.5 text-neon-violet" /> Model Engine
                  </span>
                  <span className="font-mono text-neon-cyan font-semibold text-[11px]">Gemini 3.6 Flash</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground flex items-center gap-1.5">
                    <Sliders className="w-3.5 h-3.5 text-neon-emerald" /> Temperature
                  </span>
                  <span className="font-mono text-foreground font-semibold">{agent.temperature}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground flex items-center gap-1.5">
                    <Database className="w-3.5 h-3.5 text-neon-magenta" /> Knowledge Base
                  </span>
                  <span className="font-mono text-emerald-400 font-semibold">Active (RAG)</span>
                </div>
              </div>

              <div>
                <span className="text-[10px] text-muted-foreground uppercase font-mono tracking-wider">Equipped Modules</span>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {agent.tools.map((tool, idx) => (
                    <span key={idx} className="bg-white/5 border border-white/10 px-2 py-1 rounded-md text-[11px] text-foreground/80 flex items-center gap-1">
                      <Sparkles className="w-2.5 h-2.5 text-neon-cyan" />
                      {tool}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'output' && (
            <div className="space-y-3 h-full flex flex-col">
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-muted-foreground uppercase font-mono tracking-wider">Live Agent Trace</span>
                <Button variant="ghost" size="sm" onClick={handleCopy} className="h-6 px-2 text-[10px] text-neon-cyan">
                  {copied ? <Check className="w-3 h-3 mr-1 text-emerald-400" /> : <Copy className="w-3 h-3 mr-1" />}
                  {copied ? 'Copied' : 'Copy'}
                </Button>
              </div>
              <div className="bg-black/60 p-3 rounded-xl border border-white/10 font-mono text-[11px] text-foreground/90 leading-relaxed overflow-y-auto max-h-60 custom-scrollbar whitespace-pre-wrap">
                {agentOutput}
              </div>
            </div>
          )}

          {activeTab === 'raw' && (
            <div className="space-y-2 font-mono text-[11px]">
              <span className="text-[10px] text-muted-foreground uppercase tracking-wider">JSON Inspector Config</span>
              <pre className="bg-black/60 p-3 rounded-xl border border-white/10 text-neon-cyan overflow-x-auto text-[10px] leading-snug">
                {JSON.stringify(
                  {
                    agent_id: agentId,
                    status: graphState ? 'initialized' : 'idle',
                    max_iterations: 3,
                    memory_buffer: "128k context window",
                    timeout_ms: 15000,
                  },
                  null,
                  2
                )}
              </pre>
            </div>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
