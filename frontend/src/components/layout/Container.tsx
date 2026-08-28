import React from 'react';
import { cn } from '../../utils/formatters';

interface ContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  maxW?: string;
}

export function Container({ className, children, maxW }: ContainerProps) {
  return (
    <div className={cn("mx-auto w-full max-w-7xl px-4 md:px-8", maxW, className)}>
      {children}
    </div>
  );
}
