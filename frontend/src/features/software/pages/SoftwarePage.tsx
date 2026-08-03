import React, { useState } from "react";
import { Package, Upload, Download } from "lucide-react";
import { Card, Button, Badge } from "../../../components/ui";

export const SoftwarePage = React.memo(function SoftwarePage() {
  const [packages] = useState([
    { id: "pkg-1", name: "Sentinel EDR Agent Installer", version: "v5.4.1", platform: "Windows", size: "42.5 MB", status: "APPROVED" },
    { id: "pkg-2", name: "Sentinel EDR Linux Daemon", version: "v5.4.0", platform: "Linux x86_64", size: "28.1 MB", status: "APPROVED" },
    { id: "pkg-3", name: "Sentinel macOS Endpoint Guard", version: "v5.3.9", platform: "macOS ARM64", size: "35.2 MB", status: "APPROVED" },
    { id: "pkg-4", name: "Custom Incident Response CLI Tool", version: "v1.2.0", platform: "Cross-Platform", size: "12.8 MB", status: "STAGING" },
  ]);

  const handleUpload = () => {
    alert("Package Upload Manager: Select your .msi, .exe, .deb, or .pkg deployment binary.");
  };

  return (
    <div className="w-full space-y-4 px-2 sm:px-4 py-2">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-container-low border-b border-outline-variant/60 p-4 rounded-xl shadow-xs">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary/10 border border-primary/30 rounded-xl flex items-center justify-center text-primary flex-shrink-0">
            <Package className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-on-surface tracking-tight">Enterprise Software Repository</h1>
            <p className="text-xs text-on-surface-variant font-medium">
              Software Packages, Automated Fleet Deployments & Version Control Catalog
            </p>
          </div>
        </div>

        <Button onClick={handleUpload} variant="primary" size="sm" leftIcon={<Upload className="h-4 w-4" />}>
          Upload Package
        </Button>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {packages.map((pkg) => (
          <Card key={pkg.id} className="p-4 bg-surface-container-low border-outline-variant space-y-3 flex flex-col justify-between">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Badge variant={pkg.status === "APPROVED" ? "success" : "warning"} size="sm" className="font-bold">
                  {pkg.status}
                </Badge>
                <span className="font-mono text-[10px] font-bold text-on-surface-variant">{pkg.platform}</span>
              </div>
              <h3 className="text-body-md font-black text-on-surface">{pkg.name}</h3>
              <div className="flex items-center justify-between font-mono text-[11px] text-on-surface-variant">
                <span>Version: {pkg.version}</span>
                <span>Size: {pkg.size}</span>
              </div>
            </div>

            <div className="pt-2 border-t border-outline-variant/30 flex items-center justify-end">
              <Button
                onClick={() => alert(`Deploying ${pkg.name} to target endpoints...`)}
                variant="outline"
                size="sm"
                leftIcon={<Download className="h-3.5 w-3.5" />}
              >
                Deploy Package
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
});
