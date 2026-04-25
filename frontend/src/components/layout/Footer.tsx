import { Container } from './Container';

export function Footer() {
  return (
    <footer className="border-t border-glass-border py-6 md:py-0">
      <Container>
        <div className="flex flex-col items-center justify-between gap-4 md:h-16 md:flex-row">
          <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
            Built with React, LangGraph, and Flask. Neuro-Agents Multi-Agent System.
          </p>
        </div>
      </Container>
    </footer>
  );
}
