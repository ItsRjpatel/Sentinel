import React from "react";
import { cn } from "../../utils/cn";
import { FolderOpen } from "lucide-react";

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export function EmptyState({
  icon = <FolderOpen className="h-10 w-10 text-on-surface-variant/40" />,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center p-8 text-center bg-surface-container-low border border-dashed border-outline-variant rounded-xl my-4",
        className
      )}
    >
      <div className="p-3 bg-surface-container-high rounded-full mb-3">{icon}</div>
      <h4 className="text-body-md font-bold text-on-surface">{title}</h4>
      {description && (
        <p className="text-body-sm text-on-surface-variant max-w-sm mt-1 mb-4">{description}</p>
      )}
      {action && <div className="mt-2">{action}</div>}
    </div>
  );
}
