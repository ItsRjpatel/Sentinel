import React, { useState } from "react";
import { X, ShieldPlus } from "lucide-react";
import { Button } from "../../../components/ui";
import { useCreateRole } from "../api/rbacApi";

interface CreateRoleModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CreateRoleModal = React.memo(function CreateRoleModal({
  isOpen,
  onClose,
}: CreateRoleModalProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const createMutation = useCreateRole();

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      alert("Role name is required.");
      return;
    }

    try {
      await createMutation.mutateAsync({ name: name.trim(), description: description.trim() });
      alert(`Role ${name} created successfully!`);
      onClose();
    } catch (err: any) {
      alert(`Failed to create role: ${err.message || "Unknown error"}`);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="w-full max-w-lg bg-surface-container-low border border-outline-variant/60 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
        <div className="p-4 border-b border-outline-variant/60 flex items-center justify-between bg-surface-container-high/60">
          <div className="flex items-center gap-2">
            <ShieldPlus className="h-5 w-5 text-primary" />
            <h3 className="text-body-md font-black text-on-surface">Create RBAC Role</h3>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-surface-container-highest text-on-surface-variant">
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4 text-xs">
          <div className="space-y-1">
            <label className="font-bold text-on-surface uppercase">Role Name *</label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full p-2.5 bg-surface-container-high border border-outline-variant/50 rounded-xl text-on-surface focus:outline-none focus:border-primary font-bold"
              placeholder="e.g. Incident Responder"
            />
          </div>

          <div className="space-y-1">
            <label className="font-bold text-on-surface uppercase">Description</label>
            <textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full p-2.5 bg-surface-container-high border border-outline-variant/50 rounded-xl text-on-surface focus:outline-none focus:border-primary"
              placeholder="Describe access privileges and capability scopes..."
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-3 border-t border-outline-variant/40">
            <Button type="button" variant="outline" size="sm" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" disabled={createMutation.isPending} className="font-extrabold shadow-xs">
              {createMutation.isPending ? "Creating..." : "Create Role"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
});
