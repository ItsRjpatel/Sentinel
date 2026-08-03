import React from "react";
import { HardDrive, Lock, RefreshCw, AlertCircle } from "lucide-react";
import { Card, Badge, LoadingSkeleton } from "../../../../components/ui";
import { useStorage } from "../api/detailsApi";

export const StorageTab = React.memo(function StorageTab({ endpointId }: { endpointId: string }) {
  const { data, isLoading, isError, refetch } = useStorage(endpointId);

  if (isLoading) {
    return <LoadingSkeleton height={360} />;
  }

  if (isError || !data) {
    return (
      <Card className="p-6 bg-error/10 border border-error/30 text-center space-y-3">
        <AlertCircle className="h-8 w-8 text-error mx-auto" />
        <p className="text-xs text-on-surface-variant font-medium">Failed to load storage inventory</p>
        <button
          onClick={() => refetch()}
          className="px-3 py-1.5 bg-error text-on-error rounded text-xs font-bold inline-flex items-center gap-1.5"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Retry
        </button>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Physical Disks Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {data.physical_disks.map((disk, idx) => (
          <Card key={idx} className="p-4 bg-surface-container-low border-outline-variant space-y-3">
            <div className="flex items-center justify-between border-b border-outline-variant/40 pb-2">
              <div className="flex items-center gap-2">
                <HardDrive className="h-5 w-5 text-primary" />
                <h4 className="font-extrabold text-on-surface text-xs">{disk.model}</h4>
              </div>
              <Badge variant={disk.health_status === "Healthy" ? "success" : "warning"} size="sm">
                {disk.health_status}
              </Badge>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <span className="text-on-surface-variant">Capacity:</span>
                <p className="font-bold text-on-surface font-mono">{disk.size_gb} GB ({disk.media_type})</p>
              </div>
              <div>
                <span className="text-on-surface-variant">Serial Number:</span>
                <p className="font-bold text-on-surface font-mono">{disk.serial_number}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Logical Volumes Table */}
      <Card className="p-0 bg-surface-container-low border-outline-variant overflow-hidden">
        <div className="p-4 border-b border-outline-variant/40 flex items-center justify-between">
          <h3 className="text-body-md font-extrabold text-on-surface">Logical Volume Partitions</h3>
          <span className="text-xs text-on-surface-variant font-medium">
            Total Capacity: <strong className="text-on-surface font-mono">{data.total_capacity_gb} GB</strong>
          </span>
        </div>

        <div className="overflow-x-auto scrollbar-none">
          <table className="w-full text-left border-collapse whitespace-nowrap text-xs">
            <thead className="bg-surface-container-high text-on-surface-variant font-bold uppercase">
              <tr>
                <th className="px-4 py-3">Drive</th>
                <th className="px-4 py-3">Volume Name</th>
                <th className="px-4 py-3">File System</th>
                <th className="px-4 py-3">Capacity / Usage</th>
                <th className="px-4 py-3">Free Space</th>
                <th className="px-4 py-3">BitLocker Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/30 font-medium">
              {data.logical_volumes.map((vol, idx) => {
                const usedPct = vol.capacity_gb > 0 ? Math.round((vol.used_gb / vol.capacity_gb) * 100) : 0;
                return (
                  <tr key={idx} className="hover:bg-surface-container-high/40 transition-colors">
                    <td className="px-4 py-3 font-mono font-bold text-primary">{vol.drive_letter}</td>
                    <td className="px-4 py-3 text-on-surface font-bold">{vol.volume_name}</td>
                    <td className="px-4 py-3 text-on-surface-variant font-mono">{vol.file_system}</td>
                    <td className="px-4 py-3 min-w-[200px]">
                      <div className="space-y-1">
                        <div className="flex justify-between text-[11px] font-bold">
                          <span>{vol.used_gb} GB used</span>
                          <span>{usedPct}%</span>
                        </div>
                        <div className="h-2 bg-surface-container-highest rounded-full overflow-hidden">
                          <div className="h-full bg-primary rounded-full" style={{ width: `${usedPct}%` }} />
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-success font-bold font-mono">{vol.free_gb} GB</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1.5 text-success font-bold">
                        <Lock className="h-3.5 w-3.5" />
                        <span>{vol.bitlocker_status}</span>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
});
