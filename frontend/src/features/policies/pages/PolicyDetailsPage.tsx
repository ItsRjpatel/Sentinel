import React from "react";
import { useParams, Link } from "react-router-dom";
import {
  ArrowLeft,
  History,
  RotateCcw,
  Code
} from "lucide-react";
import { usePolicyDetails, usePolicyVersions, useRollbackPolicy } from "../api/policiesApi";
import { Card, LoadingSkeleton } from "../../../components/ui";

export const PolicyDetailsPage: React.FC = () => {
  const { id = "" } = useParams<{ id: string }>();
  const { data: policy, isLoading: policyLoading } = usePolicyDetails(id);
  const { data: versions = [], isLoading: versionsLoading } = usePolicyVersions(id);
  const rollbackMutation = useRollbackPolicy();

  if (policyLoading) {
    return (
      <div className="p-6 space-y-4">
        <LoadingSkeleton height={120} />
        <LoadingSkeleton height={300} />
      </div>
    );
  }

  if (!policy) {
    return (
      <div className="p-12 text-center text-on-surface-variant">
        <h3 className="text-body-md font-bold text-on-surface">Policy Profile Not Found</h3>
        <Link to="/policies" className="text-primary text-xs font-bold hover:underline mt-2 inline-block">
          Return to Policies List
        </Link>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 bg-surface min-h-screen text-on-surface">
      {/* Top Header */}
      <div className="flex items-center gap-4">
        <Link
          to="/policies"
          className="p-2 bg-surface-container hover:bg-surface-container-high rounded-xl text-on-surface-variant transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 bg-primary/10 text-primary font-mono text-[10px] font-bold rounded uppercase border border-primary/20">
              {policy.category} • v{policy.version}
            </span>
            <h1 className="text-body-lg font-black text-on-surface">{policy.name}</h1>
          </div>
          <p className="text-xs text-on-surface-variant">{policy.description || "No description provided."}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: JSON Settings & Configuration Parameters */}
        <div className="lg:col-span-2 space-y-4">
          <Card className="p-5 border-outline-variant/60 space-y-3">
            <h3 className="text-body-md font-black text-on-surface flex items-center gap-2 border-b border-outline-variant/40 pb-2">
              <Code className="h-5 w-5 text-primary" /> Policy Rule Definitions & Settings Payload
            </h3>
            <pre className="p-4 bg-surface-container-highest rounded-xl text-xs font-mono text-on-surface overflow-x-auto border border-outline-variant/40 max-h-96">
              {JSON.stringify(policy.settings, null, 2)}
            </pre>
          </Card>
        </div>

        {/* Right 1 Col: Revision History & Rollback Engine */}
        <div className="space-y-4">
          <Card className="p-5 border-outline-variant/60 space-y-4">
            <h3 className="text-body-md font-black text-on-surface flex items-center gap-2 border-b border-outline-variant/40 pb-2">
              <History className="h-5 w-5 text-amber-400" /> Revision History
            </h3>

            {versionsLoading ? (
              <LoadingSkeleton height={150} />
            ) : versions.length === 0 ? (
              <p className="text-xs text-on-surface-variant text-center py-4">No history recorded.</p>
            ) : (
              <div className="space-y-2">
                {versions.map((ver) => {
                  const isCurrent = ver.version === policy.version;
                  return (
                    <div
                      key={ver.id}
                      className={`p-3 rounded-xl border transition-all text-xs space-y-1 ${
                        isCurrent
                          ? "bg-primary/10 border-primary/40 text-on-surface"
                          : "bg-surface-container border-outline-variant/40 text-on-surface-variant"
                      }`}
                    >
                      <div className="flex items-center justify-between font-mono font-bold">
                        <span className="text-primary">Version {ver.version}</span>
                        {isCurrent ? (
                          <span className="text-[10px] bg-primary text-on-primary px-1.5 py-0.2 rounded uppercase">Current</span>
                        ) : (
                          <button
                            onClick={() => rollbackMutation.mutate({ id: policy.id, version: ver.version })}
                            className="text-[10px] text-amber-400 hover:underline flex items-center gap-1 font-sans cursor-pointer"
                          >
                            <RotateCcw className="h-3 w-3" /> Rollback
                          </button>
                        )}
                      </div>

                      <p className="text-[11px] font-sans text-on-surface-variant">{ver.change_summary || "Updated settings"}</p>
                      <span className="text-[10px] font-mono text-on-surface-variant/70 block">
                        {new Date(ver.created_at).toLocaleString()}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};
