export type ShellType = "powershell" | "cmd";
export type ExecutionContext = "SYSTEM" | "User";
export type ExecutionPolicy = "Bypass" | "RemoteSigned" | "Unrestricted" | "Default";

export interface ExecutionOptions {
  shell: ShellType;
  runAs: ExecutionContext;
  timeout: number; // in seconds
  captureOutput: boolean;
  stopOnError: boolean;
  executionPolicy: ExecutionPolicy;
}

export interface TerminalLine {
  id: string;
  timestamp: string;
  type: "input" | "output" | "error" | "system" | "info";
  text: string;
  commandId?: string;
}

export interface ConsoleCommandRecord {
  id: string;
  commandType: string;
  commandText: string;
  shell: ShellType;
  status: "PENDING" | "SENT" | "RUNNING" | "SUCCESS" | "FAILED" | "TIMEOUT";
  requestedAt: string;
  startedAt?: string;
  completedAt?: string;
  durationMs?: number;
  user: string;
  exitCode?: number;
  stdout?: string;
  stderr?: string;
  result?: any;
}

export interface CommandTemplate {
  id: string;
  title: string;
  category: "Networking" | "System" | "Services" | "Processes" | "Storage" | "Windows" | "Registry" | "Security" | "Users" | "Custom";
  shell: ShellType;
  script: string;
  description: string;
  isFavorite?: boolean;
}

export interface EndpointSession {
  endpointId: string;
  hostname: string;
  osVersion?: string;
  ipAddress?: string;
  status: "online" | "offline" | "connecting";
  lastSeen?: string;
  options: ExecutionOptions;
  terminalBuffer: TerminalLine[];
  history: ConsoleCommandRecord[];
  activeCommandId?: string;
}
