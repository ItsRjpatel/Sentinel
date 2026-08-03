import React from "react";
import { Building2, Globe } from "lucide-react";
import { Card } from "../../../components/ui";

export const OrganizationPage = React.memo(function OrganizationPage() {
  const sites = [
    { name: "New York HQ", region: "us-east-1", endpoints: 450, compliant: "99.2%", risk: "Low" },
    { name: "London Regional Office", region: "eu-west-1", endpoints: 210, compliant: "98.5%", risk: "Low" },
    { name: "Tokyo Innovation Hub", region: "ap-northeast-1", endpoints: 180, compliant: "97.8%", risk: "Medium" },
    { name: "Frankfurt Data Center", region: "eu-central-1", endpoints: 120, compliant: "100%", risk: "Low" },
  ];

  return (
    <div className="w-full space-y-4 px-2 sm:px-4 py-2">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-container-low border-b border-outline-variant/60 p-4 rounded-xl shadow-xs">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary/10 border border-primary/30 rounded-xl flex items-center justify-center text-primary flex-shrink-0">
            <Building2 className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-on-surface tracking-tight">Enterprise Organization Overview</h1>
            <p className="text-xs text-on-surface-variant font-medium">
              Global Fleet Distribution, Multi-Site Deployment & Risk Topology
            </p>
          </div>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
        <Card className="p-4 bg-surface-container-low border-outline-variant space-y-1">
          <span className="text-[10px] font-bold text-on-surface-variant uppercase">Global Sites</span>
          <p className="text-2xl font-black text-primary font-mono">4 Regions</p>
        </Card>
        <Card className="p-4 bg-surface-container-low border-outline-variant space-y-1">
          <span className="text-[10px] font-bold text-on-surface-variant uppercase">Managed Fleet Assets</span>
          <p className="text-2xl font-black text-tertiary font-mono">960 Devices</p>
        </Card>
        <Card className="p-4 bg-surface-container-low border-outline-variant space-y-1">
          <span className="text-[10px] font-bold text-on-surface-variant uppercase">Average Compliance</span>
          <p className="text-2xl font-black text-success font-mono">98.8%</p>
        </Card>
        <Card className="p-4 bg-surface-container-low border-outline-variant space-y-1">
          <span className="text-[10px] font-bold text-on-surface-variant uppercase">Active High Risk Sites</span>
          <p className="text-2xl font-black text-on-surface font-mono">0 Sites</p>
        </Card>
      </div>

      {/* Sites Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sites.map((s) => (
          <Card key={s.name} className="p-4 bg-surface-container-low border-outline-variant space-y-3">
            <div className="flex items-center justify-between border-b border-outline-variant/30 pb-2">
              <h3 className="text-body-md font-black text-on-surface flex items-center gap-2">
                <Globe className="h-4 w-4 text-primary" /> {s.name}
              </h3>
              <span className="font-mono text-[10px] font-bold text-on-surface-variant bg-surface-container-high px-2 py-0.5 rounded">
                {s.region}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-2 text-xs font-medium">
              <div>
                <span className="text-on-surface-variant">Endpoints:</span>
                <p className="font-black text-on-surface font-mono">{s.endpoints}</p>
              </div>
              <div>
                <span className="text-on-surface-variant">Compliance:</span>
                <p className="font-black text-success font-mono">{s.compliant}</p>
              </div>
              <div>
                <span className="text-on-surface-variant">Security Risk:</span>
                <p className="font-black text-primary font-mono">{s.risk}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
});
