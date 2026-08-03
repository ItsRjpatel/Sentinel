import React, { useState } from "react";
import { X, UserPlus } from "lucide-react";
import { Button } from "../../../components/ui";
import { useCreateUser } from "../api/usersApi";

interface CreateUserModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CreateUserModal = React.memo(function CreateUserModal({
  isOpen,
  onClose,
}: CreateUserModalProps) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [role, setRole] = useState("Analyst");

  const createMutation = useCreateUser();

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !email.trim() || !password.trim()) {
      alert("Please fill in all required fields.");
      return;
    }

    try {
      await createMutation.mutateAsync({
        username: username.trim(),
        email: email.trim(),
        password: password.trim(),
        first_name: firstName.trim() || undefined,
        last_name: lastName.trim() || undefined,
        roles: [role],
      });
      alert(`User ${username} created successfully!`);
      onClose();
    } catch (err: any) {
      alert(`Failed to create user: ${err.message || "Unknown error"}`);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="w-full max-w-lg bg-surface-container-low border border-outline-variant/60 rounded-2xl shadow-2xl overflow-hidden flex flex-col">
        <div className="p-4 border-b border-outline-variant/60 flex items-center justify-between bg-surface-container-high/60">
          <div className="flex items-center gap-2">
            <UserPlus className="h-5 w-5 text-primary" />
            <h3 className="text-body-md font-black text-on-surface">Provision Console Operator</h3>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-surface-container-highest text-on-surface-variant">
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4 text-xs">
          <div className="space-y-1">
            <label className="font-bold text-on-surface uppercase">Username *</label>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full p-2.5 bg-surface-container-high border border-outline-variant/50 rounded-xl text-on-surface focus:outline-none focus:border-primary font-bold"
              placeholder="e.g. jdoe"
            />
          </div>

          <div className="space-y-1">
            <label className="font-bold text-on-surface uppercase">Email Address *</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full p-2.5 bg-surface-container-high border border-outline-variant/50 rounded-xl text-on-surface focus:outline-none focus:border-primary font-bold"
              placeholder="e.g. jdoe@enterprise.com"
            />
          </div>

          <div className="space-y-1">
            <label className="font-bold text-on-surface uppercase">Initial Password *</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-2.5 bg-surface-container-high border border-outline-variant/50 rounded-xl text-on-surface focus:outline-none focus:border-primary font-mono"
              placeholder="••••••••••••"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <label className="font-bold text-on-surface uppercase">First Name</label>
              <input
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="w-full p-2.5 bg-surface-container-high border border-outline-variant/50 rounded-xl text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            <div className="space-y-1">
              <label className="font-bold text-on-surface uppercase">Last Name</label>
              <input
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="w-full p-2.5 bg-surface-container-high border border-outline-variant/50 rounded-xl text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="font-bold text-on-surface uppercase">Primary Role</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full p-2.5 bg-surface-container-high border border-outline-variant/50 rounded-xl text-on-surface font-extrabold focus:outline-none focus:border-primary"
            >
              <option value="Administrator">Administrator</option>
              <option value="Analyst">Analyst</option>
              <option value="Operator">Operator</option>
            </select>
          </div>

          <div className="flex items-center justify-end gap-2 pt-3 border-t border-outline-variant/40">
            <Button type="button" variant="outline" size="sm" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm" disabled={createMutation.isPending} className="font-extrabold shadow-xs">
              {createMutation.isPending ? "Creating..." : "Create Account"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
});
