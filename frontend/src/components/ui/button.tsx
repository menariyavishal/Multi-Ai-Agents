import * as React from "react"
import { VariantProps, cva } from "class-variance-authority"
import { cn } from "../../utils/formatters"
import { motion } from "framer-motion"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium ring-offset-background transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 select-none",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90 shadow-md shadow-primary/20",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90 shadow-md shadow-destructive/20",
        outline: "border border-input bg-background/50 backdrop-blur-md hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent/60 hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
        glass: "bg-glass border border-glass-border backdrop-blur-xl hover:bg-white/10 text-foreground shadow-lg",
        cyber: "bg-gradient-to-r from-neon-violet to-neon-cyan text-black font-semibold hover:opacity-90 shadow-lg shadow-neon-cyan/20 border border-neon-cyan/40",
        unity: "bg-unity-panel border border-neon-cyan/30 text-neon-cyan hover:bg-neon-cyan/10 hover:border-neon-cyan/60 shadow-lg shadow-neon-cyan/10 font-mono tracking-wide",
        neon: "bg-neon-violet/20 border border-neon-violet/40 text-neon-violet hover:bg-neon-violet/30 hover:border-neon-violet/80 shadow-lg shadow-neon-violet/20"
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-12 rounded-xl px-8 text-base",
        icon: "h-9 w-9 p-0",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.97 }}
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...(props as any)}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
