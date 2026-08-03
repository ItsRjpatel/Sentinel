import React from "react";
import { Cpu, Server, HardDrive, KeyRound, ShieldCheck, RefreshCw, AlertCircle } from "lucide-react";
import { Card, LoadingSkeleton } from "../../../../components/ui";
import { useHardware } from "../api/detailsApi";

export const HardwareTab = React.memo(function HardwareTab({ endpointId }: { endpointId: string }) {
  const { data, isLoading, isError, refetch } = useHardware(endpointId);

  if (isLoading) {
    return <LoadingSkeleton height={320} />;
  }

  if (isError || !data) {
    return (
      <Card className="p-6 bg-error/10 border border-error/30 text-center space-y-3">
        <AlertCircle className="h-8 w-8 text-error mx-auto" />
        <p className="text-xs text-on-surface-variant font-medium">Failed to load hardware specifications</p>
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
    <Card className="p-5 bg-surface-container-low border-outline-variant space-y-4">
      <h3 className="text-body-md font-extrabold text-on-surface border-b border-outline-variant/40 pb-2">
        Hardware Specifications & Motherboard Details
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
        <div className="p-3 bg-surface-container-high rounded-lg border border-outline-variant/30 space-y-1">
          <div className="flex items-center gap-2 text-primary font-bold">
            <Cpu className="h-4 w-4" /> Processor (CPU)
          </div>
          <p className="font-extrabold text-on-surface">{data.cpu_name}</p>
          <p className="text-on-surface-variant">{data.cpu_cores} Cores / {data.logical_processors} Threads</p>
        </div>

        <div className="p-3 bg-surface-container-high rounded-lg border border-outline-variant/30 space-y-1">
          <div className="flex items-center gap-2 text-tertiary font-bold">
            <Server className="h-4 w-4" /> System RAM
          </div>
          <p className="font-extrabold text-on-surface">{data.installed_ram_gb} GB Installed</p>
          <p className="text-on-surface-variant">DDR4 High-Speed RAM</p>
        </div>

        <div className="p-3 bg-surface-container-high rounded-lg border border-outline-variant/30 space-y-1">
          <div className="flex items-center gap-2 text-success font-bold">
            <HardDrive className="h-4 w-4" /> Motherboard & BIOS
          </div>
          <p className="font-extrabold text-on-surface">{data.motherboard}</p>
          <p className="text-on-surface-variant">{data.bios_manufacturer} v{data.bios_version}</p>
        </div>

        <div className="p-3 bg-surface-container-high rounded-lg border border-outline-variant/30 space-y-1">
          <div className="flex items-center gap-2 text-primary font-bold">
            <KeyRound className="h-4 w-4" /> TPM Chip
          </div>
          <p className="font-extrabold text-on-surface">TPM Version {data.tpm_version}</p>
          <p className="text-on-surface-variant">Hardware Cryptographic Processor</p>
        </div>

        <div className="p-3 bg-surface-container-high rounded-lg border border-outline-variant/30 space-y-1">
          <div className="flex items-center gap-2 text-success font-bold">
            <ShieldCheck className="h-4 w-4" /> Secure Boot State
          </div>
          <p className="font-extrabold text-on-surface">{data.secure_boot_enabled ? "Enabled & Active" : "Disabled"}</p>
          <p className="text-on-surface-variant">UEFI Boot Signature Validation</p>
        </div>

        <div className="p-3 bg-surface-container-high rounded-lg border border-outline-variant/30 space-y-1">
          <div className="flex items-center gap-2 text-on-surface-variant font-bold">
            <Server className="h-4 w-4" /> Graphics Processing (GPU)
          </div>
          <p className="font-extrabold text-on-surface">{data.gpu_name}</p>
          <p className="text-on-surface-variant">{data.is_virtual ? "Hypervisor Virtual Machine" : "Physical Hardware"}</p>
        </div>
      </div>
    </Card>
  );
});
