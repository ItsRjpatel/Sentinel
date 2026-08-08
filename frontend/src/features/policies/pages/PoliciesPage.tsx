import React, { useState } from "react";
import { Link } from "react-router-dom";
import {
  ShieldCheck,
  Plus,
  Trash2,
  Copy,
  ExternalLink,
  Shield,
  Lock,
  Usb,
  Key,
  RefreshCw,
  Tv,
  Zap
} from "lucide-react";
// import { usePoliciesList, useCreatePolicy, useDeletePolicy, useClonePolicy } from "../api/policiesApi";
import { Card, LoadingSkeleton } from "../../../components/ui";

const CATEGORY_ICONS: Record<string, React.ElementType> = {
  Defender: ShieldCheck,
  Firewall: Shield,
  BitLocker: Lock,
  USB: Usb,
  Password: Key,
  WindowsUpdate: RefreshCw,
  RDP: Tv,
  Power: Zap
};

export const PoliciesPage: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");
  const isLoading = false;
  const policies: any[] = [];
  
  return (
    <div className="p-6 space-y-6 bg-surface min-h-screen text-on-surface">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-body-lg font-black tracking-tight text-on-surface flex items-center gap-2">
            <ShieldCheck className="h-7 w-7 text-primary" /> Security Policy Engine
          </h1>
          <p className="text-xs text-on-surface-variant">
            Manage & deploy Windows Defender, Firewall, BitLocker, USB, Password, & Update security policies.
          </p>
        </div>

        <button
          disabled
          className="flex items-center gap-1.5 px-4 py-2 bg-primary/50 text-on-primary/50 font-bold text-xs rounded-xl cursor-not-allowed"
        >
          <Plus className="h-4 w-4" /> Create Policy
        </button>
      </div>

      {/* Category Filter Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        {["ALL", "Defender", "Firewall", "BitLocker", "USB", "Password", "WindowsUpdate", "RDP", "Power"].map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1.5 text-xs font-bold rounded-xl border transition-all cursor-pointer whitespace-nowrap ${
              selectedCategory === cat
                ? "bg-primary/10 border-primary text-primary"
                : "bg-surface-container border-outline-variant text-on-surface-variant hover:text-on-surface"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Policies Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <LoadingSkeleton height={180} />
          <LoadingSkeleton height={180} />
          <LoadingSkeleton height={180} />
        </div>
      ) : policies.length === 0 ? (
        <Card className="p-12 text-center text-on-surface-variant border-dashed">
          <ShieldCheck className="h-12 w-12 text-primary mx-auto mb-3 opacity-40" />
          <h3 className="text-body-md font-bold text-on-surface mb-1">Feature Planned for Future Release</h3>
          <p className="text-xs">The security policy deployment engine is currently in development.</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {policies.map((pol) => {
            const IconComp = CATEGORY_ICONS[pol.category] || ShieldCheck;
            return (
              <Card key={pol.id} className="p-5 border-outline-variant/60 hover:border-primary/50 transition-all space-y-4 flex flex-col justify-between">
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <div className="p-2 bg-primary/10 rounded-lg text-primary">
                        <IconComp className="h-5 w-5" />
                      </div>
                      <div>
                        <span className="px-2 py-0.5 bg-surface-container-high text-on-surface-variant font-mono text-[9px] font-bold rounded border border-outline-variant/40">
                          v{pol.version} • {pol.status}
                        </span>
                        <h3 className="text-body-md font-black text-on-surface mt-1">{pol.name}</h3>
                      </div>
                    </div>

                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => {}}
                        className="p-1.5 hover:bg-surface-container-highest text-on-surface-variant hover:text-primary rounded-lg transition-colors cursor-pointer"
                        title="Clone Policy"
                      >
                        <Copy className="h-3.5 w-3.5" />
                      </button>
                      <button
                        onClick={() => {}}
                        className="p-1.5 hover:bg-error/10 text-on-surface-variant hover:text-error rounded-lg transition-colors cursor-pointer"
                        title="Delete Policy"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>

                  <p className="text-xs text-on-surface-variant line-clamp-2 mt-2">
                    {pol.description || "No description provided."}
                  </p>
                </div>

                <div className="pt-3 border-t border-outline-variant/40 flex items-center justify-between">
                  <span className="text-[10px] text-on-surface-variant font-mono">
                    Updated: {new Date(pol.updated_at).toLocaleDateString()}
                  </span>

                  <Link
                    to={`/policies/${pol.id}`}
                    className="px-3 py-1 bg-surface-container-high hover:bg-surface-container-highest text-on-surface text-xs font-bold rounded-lg flex items-center gap-1 transition-colors cursor-pointer"
                  >
                    <span>Edit Profile</span>
                    <ExternalLink className="h-3 w-3 text-primary" />
                  </Link>
                </div>
              </Card>
            );
          })}
        </div>
      )}


    </div>
  );
};
