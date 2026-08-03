import React from "react";
import { cn } from "../../utils/cn";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "error" | "info" | "outline";
  size?: "sm" | "md";
}

export function Badge({
  className,
  variant = "default",
  size = "md",
  children,
  ...props
}: BadgeProps) {
  const baseStyles = "inline-flex items-center font-medium rounded-full uppercase tracking-wider select-none";

  const variants = {
    default: "bg-surface-container-high text-on-surface-variant border border-outline-variant/50",
    success: "bg-primary/15 text-primary border border-primary/30",
    warning: "bg-tertiary/15 text-tertiary border border-tertiary/30",
    error: "bg-error/15 text-error border border-error/30",
    info: "bg-secondary/15 text-secondary border border-secondary/30",
    outline: "bg-transparent text-on-surface-variant border border-outline-variant",
  };

  const sizes = {
    sm: "text-[10px] px-2 py-0.5 gap-1",
    md: "text-label-sm px-2.5 py-1 gap-1.5",
  };

  return (
    <span className={cn(baseStyles, variants[variant], sizes[size], className)} {...props}>
      {children}
    </span>
  );
}
