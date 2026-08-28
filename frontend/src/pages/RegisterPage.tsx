import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { UnityParticleCanvas } from '../components/ui/UnityParticleCanvas';
import { BrainCircuit, User, Mail, Lock, Sparkles, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

export function RegisterPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { register: registerUser } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      await registerUser(username, email, password);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || 'Failed to register operator');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="relative min-h-[calc(100vh-4rem)] flex items-center justify-center p-4">
      <UnityParticleCanvas />

      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.5, type: 'spring' }}
        className="w-full max-w-md unity-panel rounded-3xl p-8 border border-neon-violet/30 shadow-2xl relative z-10 space-y-6"
      >
        {/* Header */}
        <div className="text-center space-y-3">
          <div className="inline-flex p-3 rounded-2xl bg-neon-violet/10 border border-neon-violet/30 text-neon-violet neon-glow-violet mb-1">
            <BrainCircuit className="h-8 w-8" />
          </div>
          <h1 className="text-2xl font-bold font-heading text-foreground">Operator Registration</h1>
          <p className="text-xs font-mono text-muted-foreground">CREATE NEW OPERATOR PROFILE FOR MULTI-AGENT ENGINE</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-mono text-neon-violet flex items-center gap-1.5">
              <User className="w-3.5 h-3.5" /> Operator Username
            </label>
            <Input
              type="text"
              placeholder="operator_one"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="bg-black/60 border-white/15 focus:border-neon-violet focus:ring-neon-violet/20 h-11 text-sm font-sans"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-mono text-neon-cyan flex items-center gap-1.5">
              <Mail className="w-3.5 h-3.5" /> Email Address
            </label>
            <Input
              type="email"
              placeholder="operator@neuro-agents.ai"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="bg-black/60 border-white/15 focus:border-neon-cyan focus:ring-neon-cyan/20 h-11 text-sm font-sans"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-mono text-neon-magenta flex items-center gap-1.5">
              <Lock className="w-3.5 h-3.5" /> Security Password
            </label>
            <Input
              type="password"
              placeholder="••••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="bg-black/60 border-white/15 focus:border-neon-magenta focus:ring-neon-magenta/20 h-11 text-sm font-sans"
            />
          </div>

          {error && (
            <p className="text-xs text-destructive font-mono bg-destructive/10 p-3 rounded-lg border border-destructive/20">{error}</p>
          )}

          <Button 
            type="submit" 
            disabled={isSubmitting} 
            variant="cyber"
            size="lg"
            className="w-full font-mono uppercase tracking-wider font-bold shadow-lg shadow-neon-violet/20 h-12 flex items-center justify-center space-x-2"
          >
            <span>{isSubmitting ? 'Provisioning Account...' : 'Initialize Operator Profile'}</span>
            <ArrowRight className="w-4 h-4 text-black" />
          </Button>
        </form>

        <div className="pt-4 border-t border-white/10 text-center text-xs">
          <span className="text-muted-foreground">Already registered? </span>
          <Link to="/login" className="text-neon-cyan font-semibold hover:underline">
            Log in to existing profile
          </Link>
        </div>
      </motion.div>
    </div>
  );
}