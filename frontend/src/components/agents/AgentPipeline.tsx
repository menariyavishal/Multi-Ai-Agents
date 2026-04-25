import { Map, Search, LineChart, PenTool, CheckCircle, ArrowRight } from 'lucide-react';
import { AgentNode, AgentState } from './AgentNode';
import { GraphState } from '../../types/graphState';
import { motion } from 'framer-motion';

// Icons for each agent
const agentConfig = [
  { id: 'planner', name: 'Planner', icon: <Map className="w-full h-full p-1" /> },
  { id: 'researcher', name: 'Researcher', icon: <Search className="w-full h-full p-1" /> },
  { id: 'analyst', name: 'Analyst', icon: <LineChart className="w-full h-full p-1" /> },
  { id: 'writer', name: 'Writer', icon: <PenTool className="w-full h-full p-1" /> },
  { id: 'reviewer', name: 'Reviewer', icon: <CheckCircle className="w-full h-full p-1" /> },
];

interface AgentPipelineProps {
  graphState: GraphState | null;
  // Currently active agent from stream, if available
  activeStreamNode?: string | null; 
}

export function AgentPipeline({ graphState, activeStreamNode }: AgentPipelineProps) {
  
  // Calculate the state for a specific agent node given current graphState and stream updates
  const getAgentState = (id: string): AgentState => {
    if (!graphState && !activeStreamNode) return 'pending';
    
    // If we're streaming and this is the active node from SSE
    if (activeStreamNode === id) return 'processing';
    
    // If the graph state says it failed
    if (graphState?.status === 'failed') return 'error';
    
    // Check if the agent has completed in previous iterations or final state
    // We assume an agent is 'completed' if the graph state has data for it 
    // or if the graphState returned agent_completion metadata
    const completed = graphState?.agent_completion?.[id as keyof typeof graphState.agent_completion];
    
    if (completed) return 'completed';
    
    // Determine the current step implicitly if no activeStreamNode
    // This connects 'pending' state transitions to actual backend values
    if (graphState) {
        if (!graphState.plan && id === 'planner') return 'processing';
        if (graphState.plan && !graphState.research_summary && id === 'researcher') return 'processing';
        if (graphState.research_summary && !graphState.analysis && id === 'analyst') return 'processing';
        if (graphState.analysis && !graphState.draft && id === 'writer') return 'processing';
        if (graphState.draft && !graphState.review && id === 'reviewer') return 'processing';
    }
    
    return 'pending';
  };

  return (
    <div className="w-full py-8">
      <div className="flex w-full items-center justify-between relative px-4 md:px-8 max-w-4xl mx-auto overflow-x-auto pb-4 hide-scrollbar">
        
        {/* Connection Line Background */}
        <div className="absolute top-8 left-16 right-16 h-1 -z-10 bg-glass-border">
          <motion.div 
            className="h-full bg-gradient-to-r from-brand-violet to-brand-cyan" 
            initial={{ width: '0%' }}
            animate={{ 
                width: (graphState?.status === 'completed' || graphState?.status === 'approved' || graphState?.status === 'needs_revision') ? '100%' : 
                       activeStreamNode ? `${(agentConfig.findIndex(a => a.id === activeStreamNode) / (agentConfig.length - 1)) * 100}%` : '0%'
            }}
            transition={{ duration: 0.5 }}
          />
        </div>

        {agentConfig.map((agent, index) => (
          <div key={agent.id} className="flex items-center flex-shrink-0 relative">
            <AgentNode
              id={agent.id}
              name={agent.name}
              icon={agent.icon}
              state={getAgentState(agent.id)}
              index={index}
            />
            {index < agentConfig.length - 1 && (
              <div className="hidden sm:block absolute left-full ml-[-20px] w-24 z-0">
                  {/* Visual spacer indicator */}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
