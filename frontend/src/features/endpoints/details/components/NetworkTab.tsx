import React from "react";
import { RefreshCw, AlertCircle } from "lucide-react";
import { Card, Badge, LoadingSkeleton } from "../../../../components/ui";
import { useNetwork } from "../api/detailsApi";

export const NetworkTab = React.memo(function NetworkTab({ endpointId }: { endpointId: string }) {
  const { data, isLoading, isError, refetch } = useNetwork(endpointId);

  if (isLoading) {
    return <LoadingSkeleton height={320} />;
  }

  if (isError || !data) {
    return (
      <Card className="p-6 bg-error/10 border border-error/30 text-center space-y-3">
        <AlertCircle className="h-8 w-8 text-error mx-auto" />
        <p className="text-xs text-on-surface-variant font-medium">Failed to load network adapters</p>
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
      {/* Primary Network Card */}
      <Card className="p-5 bg-surface-container-low border-outline-variant space-y-4">
        <h3 className="text-body-md font-extrabold text-on-surface border-b border-outline-variant/40 pb-2">
          Active Network Stack Properties
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div>
            <span className="text-on-surface-variant font-medium">Primary IPv4:</span>
            <p className="font-mono font-bold text-primary">{data.primary_ipv4}</p>
          </div>
          <div>
            <span className="text-on-surface-variant font-medium">Primary MAC:</span>
            <p className="font-mono font-bold text-on-surface">{data.primary_mac}</p>
          </div>
          <div>
            <span className="text-on-surface-variant font-medium">DNS Servers:</span>
            <p className="font-mono font-bold text-on-surface">{data.primary_dns}</p>
          </div>
          <div>
            <span className="text-on-surface-variant font-medium">Default Gateway:</span>
            <p className="font-mono font-bold text-on-surface">{data.primary_gateway}</p>
          </div>
        </div>
      </Card>

      {/* Network Adapters Table */}
      <Card className="p-0 bg-surface-container-low border-outline-variant overflow-hidden">
        <div className="p-4 border-b border-outline-variant/40 flex items-center justify-between">
          <h3 className="text-body-md font-extrabold text-on-surface">Network Interface Adapters</h3>
        </div>

        <div className="overflow-x-auto scrollbar-none">
          <table className="w-full text-left border-collapse whitespace-nowrap text-xs">
            <thead className="bg-surface-container-high text-on-surface-variant font-bold uppercase">
              <tr>
                <th className="px-4 py-3">Adapter Name</th>
                <th className="px-4 py-3">MAC Address</th>
                <th className="px-4 py-3">IPv4 Address</th>
                <th className="px-4 py-3">IPv6 Address</th>
                <th className="px-4 py-3">DHCP</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/30 font-medium">
              {data.adapters.map((nic, idx) => (
                <tr key={idx} className="hover:bg-surface-container-high/40 transition-colors">
                  <td className="px-4 py-3 font-bold text-on-surface">{nic.adapter_name}</td>
                  <td className="px-4 py-3 font-mono text-on-surface-variant">{nic.mac_address}</td>
                  <td className="px-4 py-3 font-mono font-bold text-primary">{nic.ipv4}</td>
                  <td className="px-4 py-3 font-mono text-on-surface-variant text-[11px]">{nic.ipv6}</td>
                  <td className="px-4 py-3">
                    <Badge variant={nic.dhcp_enabled ? "success" : "default"} size="sm">
                      {nic.dhcp_enabled ? "DHCP On" : "Static IP"}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant={nic.operational_status === "Up" ? "success" : "default"} size="sm">
                      {nic.operational_status}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
});
