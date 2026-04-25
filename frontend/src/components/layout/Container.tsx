import React from 'react';
import { cn } from '../../utils/formatters';

export function Container({ className, children }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn("mx-auto w-full max-w-7xl px-4 md:px-8", className)}>
      {children}
    </div>
  );
}
