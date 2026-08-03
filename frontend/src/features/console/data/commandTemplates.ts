import type { CommandTemplate } from "../types/consoleTypes";

export const DEFAULT_COMMAND_TEMPLATES: CommandTemplate[] = [
  // Networking
  {
    id: "net-ipconfig-all",
    title: "Network Adapter Details",
    category: "Networking",
    shell: "cmd",
    script: "ipconfig /all",
    description: "Displays complete TCP/IP configuration for all network adapters.",
    isFavorite: true
  },
  {
    id: "net-ping-gateway",
    title: "Ping Gateway",
    category: "Networking",
    shell: "cmd",
    script: "ping 8.8.8.8 -n 4",
    description: "Tests ICMP network connectivity to external Google DNS."
  },
  {
    id: "net-tracert",
    title: "Trace Route",
    category: "Networking",
    shell: "cmd",
    script: "tracert -d 8.8.8.8",
    description: "Traces network hop path to destination IP without DNS resolution."
  },
  {
    id: "net-netstat-an",
    title: "Active Listening Ports",
    category: "Networking",
    shell: "cmd",
    script: "netstat -an | findstr LISTENING",
    description: "Lists all active open TCP listening ports on the endpoint."
  },
  {
    id: "net-route-print",
    title: "IPv4 Route Table",
    category: "Networking",
    shell: "cmd",
    script: "route print",
    description: "Displays current Windows IPv4 and IPv6 routing tables."
  },
  {
    id: "net-arp-a",
    title: "ARP Cache Table",
    category: "Networking",
    shell: "cmd",
    script: "arp -a",
    description: "Displays IP-to-Physical address translation table."
  },

  // System
  {
    id: "sys-computer-info",
    title: "System Hardware & OS Info",
    category: "System",
    shell: "powershell",
    script: "Get-ComputerInfo",
    description: "Returns comprehensive Windows OS and hardware attributes.",
    isFavorite: true
  },
  {
    id: "sys-whoami",
    title: "Active User Context",
    category: "System",
    shell: "cmd",
    script: "whoami /all",
    description: "Displays active user name, SID, groups, and privileges."
  },
  {
    id: "sys-systeminfo",
    title: "System Summary Report",
    category: "System",
    shell: "cmd",
    script: "systeminfo",
    description: "Displays OS version, BIOS, hotfixes, network cards, and memory."
  },
  {
    id: "sys-hotfixes",
    title: "Installed Windows Patches",
    category: "System",
    shell: "powershell",
    script: "Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 15",
    description: "Lists recent Windows KB security updates installed."
  },

  // Services
  {
    id: "svc-get-all",
    title: "List All Windows Services",
    category: "Services",
    shell: "powershell",
    script: "Get-Service | Sort-Object Status -Descending",
    description: "Lists all Win32 services sorted by status (Running/Stopped).",
    isFavorite: true
  },
  {
    id: "svc-running-only",
    title: "Active Running Services",
    category: "Services",
    shell: "powershell",
    script: "Get-Service | Where-Object Status -eq 'Running'",
    description: "Lists services currently in RUNNING state."
  },
  {
    id: "svc-restart-spooler",
    title: "Restart Print Spooler",
    category: "Services",
    shell: "powershell",
    script: "Restart-Service -Name Spooler -Force; Get-Service -Name Spooler",
    description: "Restarts the Windows Print Spooler service."
  },

  // Processes
  {
    id: "proc-top-cpu",
    title: "Top 15 CPU Processes",
    category: "Processes",
    shell: "powershell",
    script: "Get-Process | Sort-Object CPU -Descending | Select-Object -First 15 ID, ProcessName, CPU, WorkingSet64",
    description: "Lists top 15 processes consuming CPU time.",
    isFavorite: true
  },
  {
    id: "proc-top-memory",
    title: "Top 15 RAM Processes",
    category: "Processes",
    shell: "powershell",
    script: "Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 15 ID, ProcessName, @{Name='RAM(MB)';Expression={[math]::round($_.WorkingSet64/1MB,2)}}",
    description: "Lists top 15 memory-intensive running processes."
  },
  {
    id: "proc-tasklist",
    title: "Task List Verbose",
    category: "Processes",
    shell: "cmd",
    script: "tasklist /v",
    description: "Displays detailed process names, PIDs, session names, and status."
  },

  // Storage
  {
    id: "storage-volumes",
    title: "Drive Volumes & Free Space",
    category: "Storage",
    shell: "powershell",
    script: "Get-Volume | Select-Object DriveLetter, FileSystemLabel, DriveType, HealthStatus, @{Name='Size(GB)';Expression={[math]::round($_.Size/1GB,2)}}, @{Name='Free(GB)';Expression={[math]::round($_.SizeRemaining/1GB,2)}}",
    description: "Lists volume drive letters, health, size, and remaining free space."
  },
  {
    id: "storage-disks",
    title: "Physical Disk Hardware",
    category: "Storage",
    shell: "powershell",
    script: "Get-Disk | Select-Object Number, FriendlyName, OperationalStatus, HealthStatus, PartitionStyle, Size",
    description: "Displays physical drive models, partition styles, and disk health."
  },

  // Windows Maintenance
  {
    id: "win-sfc-check",
    title: "System File Integrity Check",
    category: "Windows",
    shell: "cmd",
    script: "sfc /verifyonly",
    description: "Scans integrity of system files without attempting repairs."
  },
  {
    id: "win-dism-check",
    title: "DISM Image Health Check",
    category: "Windows",
    shell: "cmd",
    script: "Dism /Online /Cleanup-Image /CheckHealth",
    description: "Checks whether Windows component store corruption is flagged."
  },

  // Registry
  {
    id: "reg-windows-version",
    title: "Query Windows NT Registry",
    category: "Registry",
    shell: "cmd",
    script: 'reg query "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion" /v ProductName',
    description: "Queries Windows OS Product Name from HKLM registry."
  },

  // Security
  {
    id: "sec-defender-status",
    title: "Defender Protection Status",
    category: "Security",
    shell: "powershell",
    script: "Get-MpComputerStatus | Select-Object RealTimeProtectionEnabled, AntivirusEnabled, NISSignatureVersion, QuickScanAge",
    description: "Reports Windows Defender antivirus & real-time protection state.",
    isFavorite: true
  },
  {
    id: "sec-firewall-profiles",
    title: "Firewall Profile Status",
    category: "Security",
    shell: "powershell",
    script: "Get-NetFirewallProfile | Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction",
    description: "Lists Domain, Private, and Public firewall profile enforcement."
  },
  {
    id: "sec-bitlocker",
    title: "BitLocker Volume Encryption",
    category: "Security",
    shell: "powershell",
    script: "Get-BitLockerVolume | Select-Object MountPoint, VolumeStatus, ProtectionStatus, EncryptionPercentage",
    description: "Reports BitLocker disk encryption progress & key status."
  },
  {
    id: "sec-tpm-status",
    title: "TPM Hardware Status",
    category: "Security",
    shell: "powershell",
    script: "Get-Tpm | Select-Object TpmPresent, TpmReady, TpmEnabled, TpmActivated",
    description: "Verifies Trusted Platform Module hardware presence and state."
  },

  // Users & Groups
  {
    id: "usr-local-admins",
    title: "Local Administrator Group Members",
    category: "Users",
    shell: "powershell",
    script: "Get-LocalGroupMember -Group 'Administrators'",
    description: "Lists all local user accounts with Administrator rights.",
    isFavorite: true
  },
  {
    id: "usr-local-users",
    title: "Local User Accounts",
    category: "Users",
    shell: "powershell",
    script: "Get-LocalUser | Select-Object Name, Enabled, PasswordRequired, LastLogon",
    description: "Lists local user accounts, enabled status, and last logon date."
  }
];
