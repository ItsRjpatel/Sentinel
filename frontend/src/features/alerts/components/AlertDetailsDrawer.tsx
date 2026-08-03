import React, { useState } from "react";
import { X, ShieldAlert, Monitor, User, MessageSquare, Send, CheckCircle2 } from "lucide-react";
import { Card, Badge, LoadingSkeleton, Button } from "../../../components/ui";
import { useAlertDetails, useAddNote } from "../api/alertsApi";

interface AlertDetailsDrawerProps {
  alertId: string | null;
  onClose: () => void;
}

export const AlertDetailsDrawer = React.memo(function AlertDetailsDrawer({
  alertId,
  onClose,
}: AlertDetailsDrawerProps) {
  const [newNote, setNewNote] = useState("");
  const { data: alert, isLoading } = useAlertDetails(alertId || "");
  const addNoteMutation = useAddNote();

  if (!alertId) return null;

  const handleAddNoteSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newNote.trim()) return;

    try {
      await addNoteMutation.mutateAsync({ id: alertId, note: newNote.trim() });
      setNewNote("");
    } catch (err: any) {
      window.alert(`Failed to add note: ${err.message || "Unknown error"}`);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex justify-end transition-opacity">
      <div className="w-full max-w-2xl bg-surface-container-low border-l border-outline-variant shadow-2xl flex flex-col h-full overflow-y-auto scrollbar-none">
        {/* Header */}
        <div className="p-4 border-b border-outline-variant/60 flex items-center justify-between bg-surface-container-high/60 sticky top-0 z-10">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-error" />
            <div>
              <h3 className="text-body-md font-black text-on-surface">Security Alert Investigation</h3>
              <p className="text-[11px] font-mono text-on-surface-variant">ID: {alertId}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-surface-container-highest text-on-surface-variant">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Body */}
        {isLoading || !alert ? (
          <div className="p-6">
            <LoadingSkeleton height={400} />
          </div>
        ) : (
          <div className="p-6 space-y-6 text-xs">
            {/* Title & Status Card */}
            <Card className="p-4 bg-surface-container border-outline-variant/50 space-y-3">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h4 className="text-body-md font-black text-on-surface">{alert.title}</h4>
                  <p className="text-on-surface-variant font-medium mt-1">{alert.description}</p>
                </div>
                <Badge variant={alert.severity.toLowerCase() === "critical" ? "error" : "warning"}>
                  {alert.severity}
                </Badge>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 border-t border-outline-variant/30 font-medium">
                <div>
                  <span className="text-on-surface-variant">Category:</span>
                  <p className="font-bold text-on-surface">{alert.category}</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Status:</span>
                  <p className="font-bold text-primary uppercase">{alert.status}</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Assigned Analyst:</span>
                  <p className="font-bold text-on-surface">{alert.assigned_analyst || "Unassigned"}</p>
                </div>
                <div>
                  <span className="text-on-surface-variant">Created Time:</span>
                  <p className="font-mono text-on-surface">{new Date(alert.created_at).toLocaleTimeString()}</p>
                </div>
              </div>
            </Card>

            {/* Endpoint Context Card */}
            <div className="space-y-2">
              <h4 className="font-black uppercase text-on-surface flex items-center gap-1.5">
                <Monitor className="h-4 w-4 text-primary" /> Affected Endpoint Details
              </h4>
              <div className="p-3 bg-surface-container-high rounded-xl border border-outline-variant/40 flex items-center justify-between">
                <div>
                  <p className="font-bold text-on-surface text-sm">{alert.endpoint_name}</p>
                  <p className="font-mono text-[11px] text-on-surface-variant">ID: {alert.endpoint_id || "N/A"}</p>
                </div>
              </div>
            </div>

            {/* Resolution History if resolved */}
            {alert.resolution_notes && (
              <div className="p-3.5 bg-success/15 border border-success/30 rounded-xl space-y-1">
                <h4 className="font-bold text-success flex items-center gap-1.5">
                  <CheckCircle2 className="h-4 w-4" /> Resolution Summary
                </h4>
                <p className="font-medium text-on-surface">{alert.resolution_notes}</p>
              </div>
            )}

            {/* Investigation Notes List */}
            <div className="space-y-3">
              <h4 className="font-black uppercase text-on-surface flex items-center gap-1.5">
                <MessageSquare className="h-4 w-4 text-primary" /> Analyst Investigation Notes ({alert.notes.length})
              </h4>

              {alert.notes.length === 0 ? (
                <div className="p-4 bg-surface-container-high rounded-xl text-center text-on-surface-variant font-medium">
                  No investigation notes recorded yet.
                </div>
              ) : (
                <div className="space-y-2 max-h-48 overflow-y-auto scrollbar-none">
                  {alert.notes.map((n, i) => (
                    <div key={i} className="p-3 bg-surface-container-high rounded-xl border border-outline-variant/30 space-y-1">
                      <div className="flex items-center justify-between font-bold text-on-surface">
                        <span className="flex items-center gap-1">
                          <User className="h-3 w-3 text-primary" /> {n.author}
                        </span>
                        <span className="font-mono text-[10px] text-on-surface-variant">
                          {new Date(n.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-on-surface-variant font-medium">{n.content}</p>
                    </div>
                  ))}
                </div>
              )}

              {/* Add Note Form */}
              <form onSubmit={handleAddNoteSubmit} className="flex gap-2 pt-1">
                <input
                  type="text"
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  placeholder="Type an investigation note..."
                  className="flex-1 p-2 bg-surface-container-high border border-outline-variant/60 rounded-xl text-on-surface focus:outline-none focus:border-primary"
                />
                <Button type="submit" variant="primary" size="sm" disabled={addNoteMutation.isPending || !newNote.trim()}>
                  <Send className="h-3.5 w-3.5" /> Note
                </Button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
});
