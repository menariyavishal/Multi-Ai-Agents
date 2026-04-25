import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { Button } from '../ui/button';
import { Container } from './Container';
import { BrainCircuit, LogOut } from 'lucide-react';

export function Header() {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-glass-border bg-background/60 backdrop-blur-xl supports-[backdrop-filter]:bg-background/40">
      <Container>
        <div className="flex h-16 items-center justify-between">
          <Link to="/" className="flex items-center space-x-2">
            <BrainCircuit className="h-6 w-6 text-brand-cyan" />
            <span className="font-bold font-heading inline-block bg-gradient-to-r from-brand-violet to-brand-cyan bg-clip-text text-transparent">
              Neuro-Agents
            </span>
          </Link>
          
          <nav className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link to="/history" className="text-sm font-medium transition-colors hover:text-primary">
                  History
                </Link>
                <div className="flex items-center space-x-4 ml-4 pl-4 border-l border-glass-border">
                  <span className="text-sm text-muted-foreground">{user?.username}</span>
                  <Button variant="ghost" size="sm" onClick={logout} className="text-destructive/80 hover:text-destructive hover:bg-destructive/10">
                    <LogOut className="h-4 w-4 mr-2" />
                    Logout
                  </Button>
                </div>
              </>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost" size="sm">Log in</Button>
                </Link>
                <Link to="/register">
                  <Button variant="glass" size="sm" className="bg-brand-violet/20 hover:bg-brand-violet/30 border-brand-violet/30 text-white">
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
