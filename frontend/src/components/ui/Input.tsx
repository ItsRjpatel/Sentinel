import React from "react";
import { cn } from "../../utils/cn";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, leftIcon, rightIcon, id, ...props }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, "-") : undefined);

    return (
      <div className="w-full space-y-1.5">
        {label && (
          <label htmlFor={inputId} className="block text-label-md font-medium text-on-surface">
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          {leftIcon && (
            <div className="absolute left-3 text-on-surface-variant flex items-center pointer-events-none">
              {leftIcon}
            </div>
          )}
          <input
            id={inputId}
            ref={ref}
            className={cn(
              "w-full bg-surface-container-high border border-outline-variant text-on-surface placeholder:text-on-surface-variant/60 rounded-lg py-2 text-body-sm transition-all duration-200 focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary",
              leftIcon ? "pl-10" : "pl-3.5",
              rightIcon ? "pr-10" : "pr-3.5",
              error && "border-error focus:ring-error focus:border-error",
              className
            )}
            {...props}
          />
          {rightIcon && (
            <div className="absolute right-3 text-on-surface-variant flex items-center">
              {rightIcon}
            </div>
          )}
        </div>
        {error && <p className="text-label-sm text-error mt-1">{error}</p>}
      </div>
    );
  }
);

Input.displayName = "Input";
