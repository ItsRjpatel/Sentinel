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
import { usePoliciesList, useCreatePolicy, useDeletePolicy, useClonePolicy } from "../api/policiesApi";
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
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [name, setName] = useState("");
  const [category, setCategory] = useState("Defender");
  const [description, setDescription] = useState("");

  const { data: policies = [], isLoading } = usePoliciesList(
    selectedCategory === "ALL" ? undefined : selectedCategory
  );

  const createMutation = useCreatePolicy();
  const deleteMutation = useDeletePolicy();
  const cloneMutation = useClonePolicy();

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    await createMutation.mutateAsync({
      name,
      category,
      description,
      settings: { enabled: true, mode: "Enforce" }
    });
    setName("");
    setDescription("");
    setIsCreateOpen(false);
  };

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
          onClick={() => setIsCreateOpen(true)}
          className="flex items-center gap-1.5 px-4 py-2 bg-primary text-on-primary font-bold text-xs rounded-xl shadow-md hover:opacity-90 transition-all cursor-pointer"
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
          <h3 className="text-body-md font-bold text-on-surface mb-1">No Security Policies Found</h3>
          <p className="text-xs">Create your first policy to enforce configuration profiles across your Windows endpoints.</p>
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
                        onClick={() => cloneMutation.mutate({ id: pol.id, newName: `${pol.name} (Copy)` })}
                        className="p-1.5 hover:bg-surface-container-highest text-on-surface-variant hover:text-primary rounded-lg transition-colors cursor-pointer"
                        title="Clone Policy"
                      >
                        <Copy className="h-3.5 w-3.5" />
                      </button>
                      <button
                        onClick={() => deleteMutation.mutate(pol.id)}
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

      {/* Create Policy Modal */}
      {isCreateOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <form onSubmit={handleCreate} className="w-full max-w-md bg-surface-container-low border border-outline-variant rounded-2xl p-6 space-y-4 shadow-2xl">
            <h3 className="text-body-md font-black text-on-surface">Create Security Policy Profile</h3>

            <div className="space-y-1">
              <label className="text-xs font-bold text-on-surface">Policy Name</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="E.g. Windows Defender Real-Time Protection"
                className="w-full p-2.5 bg-surface-container border border-outline-variant rounded-xl text-xs text-on-surface focus:outline-none focus:border-primary"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-bold text-on-surface">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full p-2.5 bg-surface-container border border-outline-variant rounded-xl text-xs text-on-surface focus:outline-none focus:border-primary"
              >
                <option value="Defender">Windows Defender Antivirus</option>
                <option value="Firewall">Windows Defender Firewall</option>
                <option value="BitLocker">BitLocker Encryption</option>
                <option value="USB">USB & Removable Media Storage</option>
                <option value="Password">Account Password Policy</option>
                <option value="WindowsUpdate">Windows Update Patching</option>
                <option value="RDP">Remote Desktop (RDP)</option>
                <option value="Power">Power & Sleep Settings</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-bold text-on-surface">Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Enter baseline policy intent and enforcement rules..."
                className="w-full p-2.5 bg-surface-container border border-outline-variant rounded-xl text-xs text-on-surface focus:outline-none focus:border-primary h-20"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-outline-variant/40">
              <button
                type="button"
                onClick={() => setIsCreateOpen(false)}
                className="px-4 py-2 bg-surface-container hover:bg-surface-container-high text-on-surface text-xs font-bold rounded-xl"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-primary text-on-primary text-xs font-bold rounded-xl shadow-md hover:opacity-90"
              >
                Save Policy
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
