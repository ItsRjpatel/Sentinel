# Endpoint Sentinel X – Enterprise Windows Agent Installer & Deployment Manual

---

## 1. Overview & Architecture

The **Endpoint Sentinel X Agent Installer** (`SentinelAgentSetup.exe`) is an enterprise-grade, single-file installer bundling the standalone Python 3.14+ runtime, agent communication daemons, win32 service wrappers, system tray UI, auto-updater, and GUI Enrollment Wizard.

### Key Capabilities
- **Zero Python Pre-requisites**: Target client VMs require NO Python installation.
- **Silent & GUI Deployment**: Supports silent automated mass deployment (`/S`) or interactive GUI wizard.
- **Windows Service Automation**: Configures `SentinelAgent` service with `Automatic` startup type and 3-stage failure recovery (`sc.exe failure SentinelAgent reset= 86400 actions= restart/60000/restart/120000/restart/300000`).
- **System Tray Operations**: Native tray application providing connectivity status, last sync timestamp, "Run Inventory Now", "Restart Agent", "Open Logs", "Collect Diagnostics", and "About".
- **Diagnostics Collector**: Archives agent logs (`agent.log`, `installer.log`, `service.log`), configuration, OS metrics, services, and network adapters into a timestamped ZIP file.
- **Auto Updater**: Integrates SHA256 checksum verification against server `/api/v1/agent/version` for seamless background upgrades.

---

## 2. Directory & Storage Specifications

### Target Installation Folder
```
C:\Program Files\Endpoint Sentinel\
├── SentinelAgentSetup.exe
├── SentinelAgentService.exe
└── runtime/
```

### Configuration & Data Folder
```
C:\ProgramData\EndpointSentinel\
├── config.json              # DPAPI-encrypted or secure JSON configuration
├── identity.json            # Machine hardware fingerprint & Agent UUID
└── logs/
    ├── agent.log            # Main background daemon logs (Rolling 10MB x 5)
    ├── installer.log        # Enrollment & installation logs
    └── service.log          # Windows SCM lifecycle logs
```

---

## 3. Deployment & Command Line Switches

### Interactive GUI Installation
Double-click `SentinelAgentSetup.exe` to launch the **Enrollment Wizard**.

### Silent Automated Deployment (MECM / Intune / Group Policy)
```powershell
SentinelAgentSetup.exe /S /server=http://192.168.1.20:8000 /token=YOUR_ENROLLMENT_TOKEN /dept="IT Operations"
```

### Silent Uninstallation
```powershell
SentinelAgentSetup.exe /uninstall /S
```

To preserve configuration & machine identity during uninstall:
```powershell
python -m agent.installer.uninstaller --keep-config
```

---

## 4. Building the Executable (`SentinelAgentSetup.exe`)

To compile the standalone single-file installer executable from source:

```bash
# 1. Activate virtual environment
d:\App_New_\Sentinel\.venv\Scripts\activate

# 2. Run automated PyInstaller build script
python scripts/build_installer.py
```

Output binary location: `dist/SentinelAgentSetup.exe`

---

## 5. Verification & Testing Procedure

1. **Service Registration**:
   ```cmd
   sc query SentinelAgent
   ```
2. **Heartbeat & Inventory Check**:
   Confirm client endpoint appears as **Healthy / Online** on the Sentinel X Web Console (`http://localhost:5173/endpoints`).
3. **Diagnostics Collection**:
   Click **Collect Diagnostics** from System Tray or run:
   ```python
   from agent.utils.diagnostics import collect_diagnostics_archive
   collect_diagnostics_archive()
   ```
