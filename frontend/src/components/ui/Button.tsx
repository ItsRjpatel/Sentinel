import React from "react";
import { cn } from "../../utils/cn";
import { Loader2 } from "lucide-react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = "primary",
      size = "md",
      isLoading = false,
      leftIcon,
      rightIcon,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const baseStyles = "inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-background disabled:opacity-50 disabled:cursor-not-allowed select-none rounded-lg";
    
    const variants = {
      primary: "bg-primary text-on-primary hover:opacity-90 active:scale-[0.98] shadow-sm focus:ring-primary",
      secondary: "bg-surface-container-high text-on-surface hover:bg-surface-container-highest active:scale-[0.98] focus:ring-outline",
      outline: "border border-outline-variant bg-transparent text-on-surface hover:bg-surface-container-high hover:border-outline focus:ring-outline",
      ghost: "bg-transparent text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high focus:ring-outline",
      danger: "bg-error text-on-error hover:opacity-90 active:scale-[0.98] focus:ring-error",
    };

    const sizes = {
      sm: "text-label-sm px-2.5 py-1.5 gap-1.5 min-h-[32px]",
      md: "text-body-sm px-4 py-2 gap-2 min-h-[40px]",
      lg: "text-body-md px-5 py-2.5 gap-2.5 min-h-[48px]",
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      >
        {isLoading ? (
          <Loader2 className="h-4 w-4 animate-spin flex-shrink-0" />
        ) : (
          leftIcon && <span className="flex-shrink-0">{leftIcon}</span>
        )}
        <span>{children}</span>
        {!isLoading && rightIcon && <span className="flex-shrink-0">{rightIcon}</span>}
      </button>
    );
  }
);

Button.displayName = "Button";
