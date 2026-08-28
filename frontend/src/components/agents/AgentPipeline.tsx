import { Map, Search, LineChart, PenTool, CheckCircle } from 'lucide-react';
import { AgentNode, AgentState } from './AgentNode';
import { GraphState } from '../../types/graphState';
import { motion } from 'framer-motion';

const agentConfig = [
  { id: 'planner', name: 'Planner', icon: <Map className="w-full h-full" /> },
  { id: 'researcher', name: 'Researcher', icon: <Search className="w-full h-full" /> },
  { id: 'analyst', name: 'Analyst', icon: <LineChart className="w-full h-full" /> },
  { id: 'writer', name: 'Writer', icon: <PenTool className="w-full h-full" /> },
  { id: 'reviewer', name: 'Reviewer', icon: <CheckCircle className="w-full h-full" /> },
];

interface AgentPipelineProps {
  graphState: GraphState | null;
  activeStreamNode?: string | null;
  selectedAgentId?: string | null;
  onSelectAgent?: (id: string) => void;
}

export function AgentPipeline({ graphState, activeStreamNode, selectedAgentId, onSelectAgent }: AgentPipelineProps) {
  
  const getAgentState = (id: string): AgentState => {
    if (!graphState && !activeStreamNode) return 'pending';
    if (activeStreamNode === id) return 'processing';
    if (graphState?.status === 'failed') return 'error';
    
    const completed = graphState?.agent_completion?.[id as keyof typeof graphState.agent_completion];
    if (completed) return 'completed';
    
    if (graphState) {
      if (graphState.status === 'completed' || graphState.status === 'approved' || graphState.status === 'needs_revision') {
        return 'completed';
      }
      if (!graphState.plan && id === 'planner') return 'processing';
      if (graphState.plan && !graphState.research_summary && id === 'researcher') return 'processing';
      if (graphState.research_summary && !graphState.analysis && id === 'analyst') return 'processing';
      if (graphState.analysis && !graphState.draft && id === 'writer') return 'processing';
      if (graphState.draft && !graphState.review && id === 'reviewer') return 'processing';
    }
    
    return 'pending';
  };

  const getProgressPercentage = (): number => {
    if (!graphState && !activeStreamNode) return 0;
    if (graphState?.status === 'completed' || graphState?.status === 'approved' || graphState?.status === 'needs_revision') {
      return 100;
    }
    if (activeStreamNode) {
      const idx = agentConfig.findIndex(a => a.id === activeStreamNode);
      return ((idx + 0.5) / (agentConfig.length - 1)) * 100;
    }
    return 20;
  };

  return (
    <div className="w-full py-6 relative">
      {/* Node Visualizer Graph */}
      <div className="flex w-full items-center justify-between relative px-2 sm:px-6 max-w-5xl mx-auto overflow-x-auto pb-4 custom-scrollbar">
        
        {/* Background Energy Flow Cable */}
        <div className="absolute top-1/2 left-12 right-12 h-1.5 -z-10 -translate-y-1/2 bg-black/60 rounded-full border border-white/10 overflow-hidden">
          <motion.div 
            className="h-full bg-gradient-to-r from-neon-violet via-neon-cyan to-neon-magenta shadow-lg shadow-neon-cyan/50" 
            initial={{ width: '0%' }}
            animate={{ width: `${getProgressPercentage()}%` }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
          />
        </div>

        {/* SVG Laser Motion Path */}
        <svg className="absolute inset-0 w-full h-full -z-10 pointer-events-none hidden sm:block">
          <line 
            x1="10%" 
            y1="50%" 
            x2="90%" 
            y2="50%" 
            stroke="rgba(0, 240, 255, 0.25)" 
            strokeWidth="2" 
            className="laser-path"
          />
        </svg>

        {agentConfig.map((agent, index) => (
          <div key={agent.id} className="flex items-center flex-shrink-0 relative my-2">
            <AgentNode
              id={agent.id}
              name={agent.name}
              icon={agent.icon}
              state={getAgentState(agent.id)}
              index={index}
              isSelected={selectedAgentId === agent.id}
              onSelect={onSelectAgent}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
