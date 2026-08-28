import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { Button } from '../ui/button';
import { Container } from './Container';
import { BrainCircuit, LogOut, Activity, Cpu, ShieldCheck, History } from 'lucide-react';

export function Header() {
  const { isAuthenticated, user, logout } = useAuth();
  const location = useLocation();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-neon-cyan/20 bg-unity-dark/80 backdrop-blur-2xl supports-[backdrop-filter]:bg-unity-dark/60 shadow-xl">
      <Container maxW="max-w-7xl">
        <div className="flex h-16 items-center justify-between">
          
          {/* Logo & Telemetry */}
          <div className="flex items-center space-x-6">
            <Link to="/" className="flex items-center space-x-2.5 group">
              <div className="p-2 rounded-xl bg-neon-cyan/10 border border-neon-cyan/30 text-neon-cyan group-hover:neon-glow-cyan transition-all duration-300">
                <BrainCircuit className="h-6 w-6" />
              </div>
              <div className="flex flex-col">
                <span className="font-bold font-heading text-lg tracking-tight bg-gradient-to-r from-neon-violet via-neon-cyan to-white bg-clip-text text-transparent">
                  Neuro-Agents
                </span>
                <span className="text-[10px] font-mono text-neon-cyan tracking-widest uppercase">UNITY ENGINE AI v2.5</span>
              </div>
            </Link>

            {/* System Telemetry Pill (Desktop) */}
            <div className="hidden lg:flex items-center space-x-3 bg-black/40 px-3 py-1 rounded-full border border-white/10 text-[11px] font-mono">
              <span className="flex items-center text-emerald-400">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse mr-1.5" />
                API ONLINE
              </span>
              <span className="text-white/20">|</span>
              <span className="text-muted-foreground flex items-center">
                <Activity className="w-3 h-3 text-neon-cyan mr-1" />
                ~115ms
              </span>
              <span className="text-white/20">|</span>
              <span className="text-neon-violet font-semibold flex items-center">
                <Cpu className="w-3 h-3 text-neon-violet mr-1" />
                Gemini 3.6 Flash
              </span>
            </div>
          </div>
          
          {/* Navigation Links */}
          <nav className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link to="/">
                  <Button 
                    variant={location.pathname === '/' ? 'unity' : 'ghost'} 
                    size="sm"
                    className="font-mono text-xs"
                  >
                    <Cpu className="w-3.5 h-3.5 mr-1.5" />
                    Workspace
                  </Button>
                </Link>
                
                <Link to="/history">
                  <Button 
                    variant={location.pathname === '/history' ? 'unity' : 'ghost'} 
                    size="sm"
                    className="font-mono text-xs"
                  >
                    <History className="w-3.5 h-3.5 mr-1.5 text-neon-cyan" />
                    History
                  </Button>
                </Link>

                <div className="flex items-center space-x-3 ml-2 pl-4 border-l border-white/10">
                  <div className="hidden sm:flex flex-col text-right">
                    <span className="text-xs font-semibold text-foreground">{user?.username}</span>
                    <span className="text-[10px] font-mono text-neon-cyan">PRO OPERATOR</span>
                  </div>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={logout} 
                    className="text-destructive hover:text-destructive hover:bg-destructive/10 font-mono text-xs"
                  >
                    <LogOut className="h-4 w-4 mr-1.5" />
                    Logout
                  </Button>
                </div>
              </>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost" size="sm" className="font-mono text-xs">Log in</Button>
                </Link>
                <Link to="/register">
                  <Button variant="cyber" size="sm" className="font-mono text-xs">
                    Get Started
                  </Button>
                </Link>
              </>
            )}
          </nav>

        </div>
      </Container>
    </header>
  );
}
