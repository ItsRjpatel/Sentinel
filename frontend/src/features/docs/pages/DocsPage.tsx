import React, { useState } from "react";
import { BookOpen, Search, Download, Code, ShieldCheck, Terminal, HelpCircle } from "lucide-react";
import { Card } from "../../../components/ui";

export const DocsPage = React.memo(function DocsPage() {
  const [search, setSearch] = useState("");
  const [selectedDocId, setSelectedDocId] = useState("agent-install");

  const articles = [
    {
      id: "agent-install",
      title: "Agent Deployment & Installation Guide",
      category: "Deployment",
      icon: Terminal,
      content: `
# Sentinel X EDR Agent Installation

## Overview
The Sentinel X lightweight agent runs natively on Windows, Linux, and macOS endpoints to provide real-time EDR telemetry, process monitoring, file integrity monitoring, and remote command execution capability.

## Prerequisites
- Operating System: Windows 10/11, Windows Server 2016+, Ubuntu 20.04+, RHEL 8+
- Memory: Minimum 256 MB RAM
- Disk Space: 50 MB
- Network: Outbound TCP port 443 / WebSocket (127.0.0.1:8000)

## Installation Steps (Windows PowerShell)

\`\`\`powershell
# Run PowerShell as Administrator
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri "https://sentinel.enterprise.internal/downloads/sentinel-agent-installer.exe" -OutFile "sentinel-agent-installer.exe"
.\\sentinel-agent-installer.exe /quiet /enrollment_key="snt-key-9988-7766"
\`\`\`

## Verification
Verify the agent service is running:

\`\`\`powershell
Get-Service -Name "SentinelAgent"
\`\`\`
      `,
    },
    {
      id: "api-docs",
      title: "REST API & Integration Specification",
      category: "API Reference",
      icon: Code,
      content: `
# Sentinel X REST API Reference

## Authentication
All API requests require a Bearer token header:

\`\`\`http
Authorization: Bearer <YOUR_JWT_TOKEN>
\`\`\`

## Core Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | \`/api/v1/dashboard/summary\` | Platform KPI summary metrics |
| **GET** | \`/api/v1/endpoints\` | List enrolled endpoints |
| **POST** | \`/api/v1/commands/bulk\` | Dispatch enterprise bulk command |
| **GET** | \`/api/v1/alerts\` | Retrieve security alerts |
| **GET** | \`/api/v1/audit\` | Query immutable audit logs |
      `,
    },
    {
      id: "architecture",
      title: "Clean Architecture & Security Blueprint",
      category: "Architecture",
      icon: ShieldCheck,
      content: `
# System Architecture Blueprint

## Architectural Layers
- **Backend**: FastAPI Async Layered Hexagonal/Clean Architecture with SQLAlchemy 2.0 Async engine.
- **Frontend**: React 18, Vite, TanStack Query (React Query) v5, Lucide Icons, and Tailwind CSS.
- **Agent**: Modular Python 3.14 EDR engine with asynchronous collector pipeline and subprocess executor.
- **Security**: OAuth2 JWT Bearer tokens, Argon2/Bcrypt password hashing, and granular RBAC permission matrix.
      `,
    },
    {
      id: "faq",
      title: "Troubleshooting & Frequently Asked Questions",
      category: "FAQ",
      icon: HelpCircle,
      content: `
# Troubleshooting & FAQ

### Q: Why is my endpoint showing "Offline"?
A: Ensure the SentinelAgent background service is active and hasn't been blocked by network firewall rules targeting WebSocket connections on port 8000.

### Q: How do I rotate agent enrollment keys?
A: Navigate to **System Settings -> Agent Config** and click "Regenerate Key". All new agent installations will require the newly generated key.
      `,
    },
  ];

  const filteredArticles = articles.filter(
    (a) =>
      a.title.toLowerCase().includes(search.toLowerCase()) ||
      a.category.toLowerCase().includes(search.toLowerCase())
  );

  const selectedArticle = articles.find((a) => a.id === selectedDocId) || articles[0];

  const downloadPdf = () => {
    const dataStr = "data:text/markdown;charset=utf-8," + encodeURIComponent(selectedArticle.content);
    const link = document.createElement("a");
    link.setAttribute("href", dataStr);
    link.setAttribute("download", `${selectedArticle.id}-guide.md`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  return (
    <div className="w-full space-y-4 px-2 sm:px-4 py-2">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-container-low border-b border-outline-variant/60 p-4 rounded-xl shadow-xs">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary/10 border border-primary/30 rounded-xl flex items-center justify-center text-primary flex-shrink-0">
            <BookOpen className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-2xl font-black text-on-surface tracking-tight">Enterprise Documentation & Knowledge Base</h1>
            <p className="text-xs text-on-surface-variant font-medium">
              Deployment Guides, REST API Specifications, Architecture Blueprints & Troubleshooting
            </p>
          </div>
        </div>

        <button
          onClick={downloadPdf}
          className="px-3 py-2 bg-surface-container-high hover:bg-surface-container-highest border border-outline-variant/40 rounded-xl text-xs font-bold transition-colors flex items-center gap-1.5 text-on-surface"
        >
          <Download className="h-4 w-4 text-primary" /> Export Document
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Sidebar Nav */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 px-3 py-2 bg-surface-container-high rounded-xl border border-outline-variant/40">
            <Search className="h-4 w-4 text-on-surface-variant flex-shrink-0" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search docs..."
              className="bg-transparent border-none focus:outline-none text-xs w-full text-on-surface"
            />
          </div>

          <div className="space-y-1">
            {filteredArticles.map((art) => {
              const Icon = art.icon;
              const isSelected = selectedDocId === art.id;
              return (
                <button
                  key={art.id}
                  onClick={() => setSelectedDocId(art.id)}
                  className={`w-full text-left p-3 rounded-xl border text-xs font-bold transition-all flex items-center gap-2.5 ${
                    isSelected
                      ? "bg-primary/15 border-primary text-primary"
                      : "bg-surface-container-low border-outline-variant/40 hover:bg-surface-container-high text-on-surface"
                  }`}
                >
                  <Icon className="h-4 w-4 flex-shrink-0" />
                  <div className="truncate">
                    <p className="truncate">{art.title}</p>
                    <span className="text-[10px] text-on-surface-variant/70 uppercase font-mono">{art.category}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Content Viewer */}
        <Card className="lg:col-span-3 p-6 bg-surface-container-low border-outline-variant space-y-4">
          <div className="border-b border-outline-variant/40 pb-3 flex items-center justify-between">
            <div>
              <span className="px-2 py-0.5 rounded bg-primary/10 text-primary font-mono text-[10px] font-bold uppercase">
                {selectedArticle.category}
              </span>
              <h2 className="text-xl font-black text-on-surface pt-1">{selectedArticle.title}</h2>
            </div>
          </div>

          <div className="prose dark:prose-invert max-w-none text-xs font-medium text-on-surface leading-relaxed whitespace-pre-line font-mono bg-surface-container-high/40 p-4 rounded-xl border border-outline-variant/30">
            {selectedArticle.content}
          </div>
        </Card>
      </div>
    </div>
  );
});
