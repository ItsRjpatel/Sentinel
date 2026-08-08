import React from "react";
import {
  Calendar,
  Plus,
  Play,
  Trash2,
  RefreshCw,
  Terminal,
  ShieldCheck,
  Activity,
  Trash
} from "lucide-react";
// import { useSchedulesList, useCreateSchedule, useRunScheduleNow, useDeleteSchedule } from "../api/schedulesApi";
import { Card, LoadingSkeleton } from "../../../components/ui";

const JOB_ICONS: Record<string, React.ElementType> = {
  INVENTORY: RefreshCw,
  COMMAND: Terminal,
  POLICY_REFRESH: ShieldCheck,
  HEARTBEAT_CHECK: Activity,
  CLEANUP: Trash
};

export const SchedulesPage: React.FC = () => {

    const schedules: any[] = []; const isLoading = false;
  
  
  return (
    <div className="p-6 space-y-6 bg-surface min-h-screen text-on-surface">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-body-lg font-black tracking-tight text-on-surface flex items-center gap-2">
            <Calendar className="h-7 w-7 text-primary" /> Task Scheduling Engine
          </h1>
          <p className="text-xs text-on-surface-variant">
            Automate recurring & one-time background tasks for inventory collection, policy enforcement, & cleanup.
          </p>
        </div>

        <button
          disabled
          className="flex items-center gap-1.5 px-4 py-2 bg-primary/50 text-on-primary/50 font-bold text-xs rounded-xl cursor-not-allowed"
        >
          <Plus className="h-4 w-4" /> Schedule Task
        </button>
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <LoadingSkeleton height={180} />
          <LoadingSkeleton height={180} />
          <LoadingSkeleton height={180} />
        </div>
      ) : schedules.length === 0 ? (
        <Card className="p-12 text-center text-on-surface-variant border-dashed">
          <Calendar className="h-12 w-12 text-primary mx-auto mb-3 opacity-40" />
          <h3 className="text-body-md font-bold text-on-surface mb-1">Feature Planned for Future Release</h3>
          <p className="text-xs">Task scheduling engine is currently in development and will be available soon.</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {schedules.map((sch) => {
            const IconComp = JOB_ICONS[sch.job_type] || Calendar;
            return (
              <Card key={sch.id} className="p-5 border-outline-variant/60 hover:border-primary/50 transition-all space-y-4 flex flex-col justify-between">
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <div className="p-2 bg-primary/10 rounded-lg text-primary">
                        <IconComp className="h-5 w-5" />
                      </div>
                      <div>
                        <span className="px-2 py-0.5 bg-surface-container-high text-on-surface-variant font-mono text-[9px] font-bold rounded border border-outline-variant/40">
                          {sch.schedule_type} • {sch.status}
                        </span>
                        <h3 className="text-body-md font-black text-on-surface mt-1">{sch.name}</h3>
                      </div>
                    </div>

                    <button
                      onClick={() => {}}
                      className="p-1.5 hover:bg-error/10 text-on-surface-variant hover:text-error rounded-lg transition-colors cursor-pointer"
                      title="Delete Scheduled Job"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>

                  {sch.cron_expression && (
                    <p className="text-xs font-mono text-primary mt-2 bg-primary/5 p-1.5 rounded border border-primary/20 inline-block">
                      Cron: {sch.cron_expression}
                    </p>
                  )}
                </div>

                <div className="pt-3 border-t border-outline-variant/40 flex items-center justify-between">
                  <span className="text-[10px] text-on-surface-variant font-mono">
                    Last Run: {sch.last_run_at ? new Date(sch.last_run_at).toLocaleTimeString() : "Never"}
                  </span>

                  <button
                    onClick={() => {}}
                    className="px-3 py-1 bg-primary text-on-primary text-xs font-bold rounded-lg flex items-center gap-1 hover:opacity-90 transition-all cursor-pointer shadow-xs"
                  >
                    <Play className="h-3 w-3 fill-current" />
                    <span>Run Now</span>
                  </button>
                </div>
              </Card>
            );
          })}
        </div>
      )}


    </div>
  );
};

