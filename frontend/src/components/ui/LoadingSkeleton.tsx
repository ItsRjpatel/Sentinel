import React from "react";
import { cn } from "../../utils/cn";

export interface LoadingSkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "text" | "circular" | "rectangular";
  width?: string | number;
  height?: string | number;
}

export function LoadingSkeleton({
  className,
  variant = "rectangular",
  width,
  height,
  style,
  ...props
}: LoadingSkeletonProps) {
  const baseStyles = "animate-pulse bg-surface-container-high";

  const variants = {
    text: "h-4 rounded",
    circular: "rounded-full",
    rectangular: "rounded-xl",
  };

  return (
    <div
      className={cn(baseStyles, variants[variant], className)}
      style={{
        width,
        height,
        ...style,
      }}
      {...props}
    />
  );
}
