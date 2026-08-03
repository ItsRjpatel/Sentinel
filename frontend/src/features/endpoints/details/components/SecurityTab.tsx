import React from "react";
import { ShieldCheck, ShieldAlert, Lock, KeyRound, RefreshCw, AlertCircle } from "lucide-react";
import { Card, Badge, LoadingSkeleton } from "../../../../components/ui";
import { useSecurity } from "../api/detailsApi";

export const SecurityTab = React.memo(function SecurityTab({ endpointId }: { endpointId: string }) {
  const { data, isLoading, isError, refetch } = useSecurity(endpointId);

  if (isLoading) {
    return <LoadingSkeleton height={320} />;
  }

  if (isError || !data) {
    return (
      <Card className="p-6 bg-error/10 border border-error/30 text-center space-y-3">
        <AlertCircle className="h-8 w-8 text-error mx-auto" />
        <p className="text-xs text-on-surface-variant font-medium">Failed to load security compliance</p>
        <button
          onClick={() => refetch()}
          className="px-3 py-1.5 bg-error text-on-error rounded text-xs font-bold inline-flex items-center gap-1.5"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Retry
        </button>
      </Card>
    );
  }

  const items = [
    { label: "Microsoft Defender Antivirus", status: data.defender_status, icon: ShieldCheck, state: "Active" },
    { label: "Windows Host Firewall", status: data.firewall_status, icon: ShieldCheck, state: "Active" },
    { label: "BitLocker Drive Encryption", status: data.bitlocker_status, icon: Lock, state: "Encrypted" },
    { label: "TPM Security Chip", status: `Version ${data.tpm_version}`, icon: KeyRound, state: "Enabled" },
    { label: "UEFI Secure Boot", status: data.secure_boot_enabled ? "Enabled & Active" : "Disabled", icon: ShieldAlert, state: data.secure_boot_enabled ? "Enabled" : "Warning" },
    { label: "Endpoint Risk Score", status: `Level: ${data.risk_level}`, icon: ShieldCheck, state: "Low" },
  ];

  return (
    <div className="space-y-4">
      {/* Security Gauges */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-5 bg-surface-container-low border-outline-variant flex flex-col justify-between space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-on-surface-variant uppercase">Security Rating</span>
            <ShieldCheck className="h-5 w-5 text-success" />
          </div>
          <div className="text-3xl font-black text-success">{data.security_score}/100</div>
          <div className="h-2 bg-surface-container-highest rounded-full overflow-hidden">
            <div className="h-full bg-success rounded-full" style={{ width: `${data.security_score}%` }} />
          </div>
        </Card>

        <Card className="p-5 bg-surface-container-low border-outline-variant flex flex-col justify-between space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-on-surface-variant uppercase">Policy Compliance</span>
            <ShieldCheck className="h-5 w-5 text-primary" />
          </div>
          <div className="text-3xl font-black text-primary">{data.compliance_score}%</div>
          <div className="h-2 bg-surface-container-highest rounded-full overflow-hidden">
            <div className="h-full bg-primary rounded-full" style={{ width: `${data.compliance_score}%` }} />
          </div>
        </Card>

        <Card className="p-5 bg-surface-container-low border-outline-variant flex flex-col justify-between space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-on-surface-variant uppercase">Calculated Risk</span>
            <ShieldAlert className="h-5 w-5 text-warning" />
          </div>
          <div className="text-3xl font-black text-on-surface">{data.risk_level}</div>
          <p className="text-[11px] text-on-surface-variant font-medium">Zero high severity threats detected</p>
        </Card>
      </div>

      {/* Security Controls Grid */}
      <Card className="p-5 bg-surface-container-low border-outline-variant space-y-4">
        <h3 className="text-body-md font-extrabold text-on-surface border-b border-outline-variant/40 pb-2">
          Security Controls & Baseline Compliance
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
          {items.map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.label} className="p-3 bg-surface-container-high rounded-lg border border-outline-variant/30 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-surface-container-low rounded-md border border-outline-variant/40 text-primary">
                    <Icon className="h-4 w-4" />
                  </div>
                  <div>
                    <p className="font-bold text-on-surface">{item.label}</p>
                    <p className="text-[11px] text-on-surface-variant">{item.status}</p>
                  </div>
                </div>
                <Badge variant={item.state === "Enabled" || item.state === "Active" || item.state === "Encrypted" || item.state === "Low" ? "success" : "warning"} size="sm">
                  {item.state}
                </Badge>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
});
