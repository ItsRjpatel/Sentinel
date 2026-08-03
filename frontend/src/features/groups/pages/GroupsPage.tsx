import React, { useState } from "react";
import { Link } from "react-router-dom";
import {
  FolderKanban,
  Plus,
  Search,
  Building2,
  MapPin,
  Trash2,
  ExternalLink
} from "lucide-react";
import { useGroupsList, useCreateGroup, useDeleteGroup } from "../api/groupsApi";
import { Card, LoadingSkeleton } from "../../../components/ui";

export const GroupsPage: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newGroupName, setNewGroupName] = useState("");
  const [newGroupType, setNewGroupType] = useState<"STATIC" | "DYNAMIC">("STATIC");
  const [newDepartment, setNewDepartment] = useState("");
  const [newSite, setNewSite] = useState("");

  const { data: groups = [], isLoading } = useGroupsList(searchTerm);
  const createMutation = useCreateGroup();
  const deleteMutation = useDeleteGroup();

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newGroupName.trim()) return;
    await createMutation.mutateAsync({
      name: newGroupName,
      group_type: newGroupType,
      department: newDepartment || undefined,
      site: newSite || undefined,
    });
    setNewGroupName("");
    setIsCreateOpen(false);
  };

  return (
    <div className="p-6 space-y-6 bg-surface min-h-screen text-on-surface">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-body-lg font-black tracking-tight text-on-surface flex items-center gap-2">
            <FolderKanban className="h-7 w-7 text-primary" /> Endpoint Groups Engine
          </h1>
          <p className="text-xs text-on-surface-variant">
            Manage static & dynamic endpoint collections, site policies, tags, and compliance stats.
          </p>
        </div>

        <button
          onClick={() => setIsCreateOpen(true)}
          className="flex items-center gap-1.5 px-4 py-2 bg-primary text-on-primary font-bold text-xs rounded-xl shadow-md hover:opacity-90 transition-all cursor-pointer"
        >
          <Plus className="h-4 w-4" /> Create Group
        </button>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="h-4 w-4 absolute left-3 top-2.5 text-on-surface-variant" />
          <input
            type="text"
            placeholder="Search endpoint groups by name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 bg-surface-container border border-outline-variant rounded-xl text-xs text-on-surface placeholder:text-on-surface-variant/60 focus:outline-none focus:border-primary"
          />
        </div>
      </div>

      {/* Main Groups Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <LoadingSkeleton height={180} />
          <LoadingSkeleton height={180} />
          <LoadingSkeleton height={180} />
        </div>
      ) : groups.length === 0 ? (
        <Card className="p-12 text-center text-on-surface-variant border-dashed">
          <FolderKanban className="h-12 w-12 text-primary mx-auto mb-3 opacity-40" />
          <h3 className="text-body-md font-bold text-on-surface mb-1">No Endpoint Groups Found</h3>
          <p className="text-xs">Create your first endpoint group to apply targeted policies and monitor compliance.</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {groups.map((group) => {
            const stats = group.stats || {
              endpoint_count: 0,
              online_count: 0,
              offline_count: 0,
              compliance_percent: 100,
              health_percent: 100
            };

            return (
              <Card key={group.id} className="p-5 border-outline-variant/60 hover:border-primary/50 transition-all space-y-4 flex flex-col justify-between">
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="px-2 py-0.5 bg-primary/10 text-primary font-mono text-[10px] font-bold rounded uppercase border border-primary/20">
                        {group.group_type}
                      </span>
                      <h3 className="text-body-md font-black text-on-surface mt-1.5">{group.name}</h3>
                    </div>
                    <button
                      onClick={() => deleteMutation.mutate(group.id)}
                      className="p-1.5 hover:bg-error/10 text-on-surface-variant hover:text-error rounded-lg transition-colors cursor-pointer"
                      title="Delete Group"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>

                  <p className="text-xs text-on-surface-variant line-clamp-2 mt-2">
                    {group.description || "No description provided."}
                  </p>

                  <div className="flex flex-wrap items-center gap-3 text-[11px] text-on-surface-variant mt-3 pt-3 border-t border-outline-variant/40">
                    {group.department && (
                      <span className="flex items-center gap-1">
                        <Building2 className="h-3.5 w-3.5 text-primary" /> {group.department}
                      </span>
                    )}
                    {group.site && (
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3.5 w-3.5 text-amber-400" /> {group.site}
                      </span>
                    )}
                  </div>
                </div>

                {/* Statistics Footer */}
                <div className="pt-3 border-t border-outline-variant/40 space-y-2">
                  <div className="grid grid-cols-3 gap-2 text-center text-xs">
                    <div className="p-1.5 bg-surface-container rounded border border-outline-variant/40">
                      <span className="text-[10px] text-on-surface-variant uppercase font-bold">Total</span>
                      <p className="font-bold text-on-surface">{stats.endpoint_count}</p>
                    </div>
                    <div className="p-1.5 bg-surface-container rounded border border-outline-variant/40">
                      <span className="text-[10px] text-emerald-400 uppercase font-bold">Online</span>
                      <p className="font-bold text-emerald-400">{stats.online_count}</p>
                    </div>
                    <div className="p-1.5 bg-surface-container rounded border border-outline-variant/40">
                      <span className="text-[10px] text-on-surface-variant uppercase font-bold">Health</span>
                      <p className="font-bold text-primary">{stats.health_percent}%</p>
                    </div>
                  </div>

                  <Link
                    to={`/groups/${group.id}`}
                    className="w-full py-1.5 bg-surface-container-high hover:bg-surface-container-highest text-on-surface text-xs font-bold rounded-lg flex items-center justify-center gap-1 transition-colors cursor-pointer"
                  >
                    <span>Inspect Group Details</span>
                    <ExternalLink className="h-3.5 w-3.5 text-primary" />
                  </Link>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Create Modal */}
      {isCreateOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <form onSubmit={handleCreate} className="w-full max-w-md bg-surface-container-low border border-outline-variant rounded-2xl p-6 space-y-4 shadow-2xl">
            <h3 className="text-body-md font-black text-on-surface">Create Endpoint Group</h3>

            <div className="space-y-1">
              <label className="text-xs font-bold text-on-surface">Group Name</label>
              <input
                type="text"
                required
                value={newGroupName}
                onChange={(e) => setNewGroupName(e.target.value)}
                placeholder="E.g. London Office Laptops"
                className="w-full p-2.5 bg-surface-container border border-outline-variant rounded-xl text-xs text-on-surface focus:outline-none focus:border-primary"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-xs font-bold text-on-surface">Type</label>
                <select
                  value={newGroupType}
                  onChange={(e) => setNewGroupType(e.target.value as any)}
                  className="w-full p-2.5 bg-surface-container border border-outline-variant rounded-xl text-xs text-on-surface focus:outline-none focus:border-primary"
                >
                  <option value="STATIC">STATIC</option>
                  <option value="DYNAMIC">DYNAMIC</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-on-surface">Department</label>
                <input
                  type="text"
                  value={newDepartment}
                  onChange={(e) => setNewDepartment(e.target.value)}
                  placeholder="IT / Sales / DevOps"
                  className="w-full p-2.5 bg-surface-container border border-outline-variant rounded-xl text-xs text-on-surface focus:outline-none focus:border-primary"
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-bold text-on-surface">Site Location</label>
              <input
                type="text"
                value={newSite}
                onChange={(e) => setNewSite(e.target.value)}
                placeholder="HQ / London / NYC"
                className="w-full p-2.5 bg-surface-container border border-outline-variant rounded-xl text-xs text-on-surface focus:outline-none focus:border-primary"
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
                Save Group
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
