import React from "react";
import { cn } from "../../utils/cn";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "flat" | "interactive";
}

export function Card({ className, variant = "default", children, ...props }: CardProps) {
  const baseStyles = "bg-surface-container-low border border-outline-variant rounded-xl p-5 transition-all duration-200";

  const variants = {
    default: "shadow-sm",
    flat: "shadow-none",
    interactive: "shadow-sm hover:border-primary/50 hover:shadow-md cursor-pointer",
  };

  return (
    <div className={cn(baseStyles, variants[variant], className)} {...props}>
      {children}
    </div>
  );
}
