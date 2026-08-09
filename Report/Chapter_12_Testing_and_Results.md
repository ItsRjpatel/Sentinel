# Chapter 12. Testing and Results

## 12.1 Introduction
Comprehensive testing was critical to ensure the reliability and stability of Endpoint Sentinel X, particularly given the concurrent nature of the backend and the low-level operating system interactions of the Windows agent. This chapter outlines the testing methodologies employed, specific test cases executed, and the final results observed during system integration.

## 12.2 Testing Strategy
The testing strategy utilized a multi-tiered approach:
1.  **Unit Testing:** Isolated testing of individual Python functions (e.g., JWT generation, password hashing) and React components.
2.  **Integration Testing:** Verifying the interaction between the FastAPI routers and the PostgreSQL database.
3.  **Functional Testing:** End-to-end testing of core workflows (Enrollment, Command Execution) using virtualized Windows environments.
4.  **Acceptance Testing:** Final manual validation of the UI against the functional requirements defined in Chapter 4.

## 12.3 Test Environment Setup
Testing was conducted using hypervisor-based virtualization (Hyper-V). 
*   **Host Machine:** Hosted the PostgreSQL database, FastAPI backend, and React development server.
*   **Virtual Machines:** Three isolated Windows 10/11 VMs were provisioned to act as remote endpoints. The custom PyInstaller executable was deployed and run as a service on these VMs.

## 12.4 Core Test Cases and Results

### 12.4.1 Test Case: Agent Enrollment
*   **Objective:** Verify that a newly installed agent can register with the backend using a valid token.
*   **Preconditions:** Backend is running. Admin generates a token from the dashboard.
*   **Steps:** 
    1. Embed token in agent config. 
    2. Start the Windows Service. 
    3. Verify the agent appears in the React dashboard.
*   **Expected Result:** Agent successfully authenticates, receives a permanent JWT, and appears online in the UI.
*   **Status:** **PASS**

### 12.4.2 Test Case: Real-Time Telemetry Upload
*   **Objective:** Verify that hardware and software inventory is populated accurately.
*   **Steps:** 
    1. Wait for the initial inventory collection loop (60 seconds after startup). 
    2. Open the Endpoint Details page in the UI.
*   **Expected Result:** CPU model, RAM, Disks, and installed software lists match the actual VM configuration exactly.
*   **Status:** **PASS**

### 12.4.3 Test Case: Remote Command Execution
*   **Objective:** Verify that a PowerShell script executes correctly and returns output.
*   **Steps:** 
    1. Queue the command `ipconfig` from the UI. 
    2. Monitor the Commands table.
*   **Expected Result:** Status transitions from `PENDING` -> `RUNNING` -> `COMPLETED`. The output correctly displays the VM's network configuration.
*   **Status:** **PASS**

### 12.4.4 Test Case: Database Concurrency and Data Integrity
*   **Objective:** Verify that multiple agents pinging the server simultaneously do not cause database locks.
*   **Steps:** 
    1. Boot all three VMs simultaneously. 
    2. Trigger mass remote command execution.
*   **Expected Result:** All transactions complete without HTTP 500 errors or Database Lock exceptions.
*   **Status:** **PASS** (Note: Initial testing with SQLite resulted in locking failures. The migration to PostgreSQL resolved all concurrency issues, resulting in a PASS).

### 12.4.5 Test Case: WebSocket Live Console Stability
*   **Objective:** Ensure the interactive shell does not crash under rapid input or unexpected disconnects.
*   **Steps:** 
    1. Open the Live Console. 
    2. Execute long-running commands (e.g., `ping -t 8.8.8.8`). 
    3. Abruptly close the browser tab.
*   **Expected Result:** The WebSocket connection terminates gracefully. The agent detects the severed socket, kills the local `cmd.exe` subprocess, and returns to a listening state without crashing the main service.
*   **Status:** **PASS**

## 12.5 Screenshot Evidence

The following screenshots validate the successful implementation of the system and its administrative modules, directly fulfilling the system requirements defined in Chapter 4.

[Screenshot Required: 01 Login]
*Figure 12.1: The secure authentication gateway for the platform.*

[Screenshot Required: 02 Dashboard]
*Figure 12.2: Global metrics showing online endpoints.*

[Screenshot Required: 03 Endpoints]
*Figure 12.3: The primary table view of enrolled assets.*

[Screenshot Required: 04 Endpoint Details]
*Figure 12.4: High-level system score and telemetry overview.*

[Screenshot Required: 05 Hardware]
*Figure 12.5: Detailed hardware inventory collected via PSutil.*

[Screenshot Required: 06 Network]
*Figure 12.6: Network adapter configuration and IP addressing details.*

[Screenshot Required: 07 Software]
*Figure 12.7: List of installed software collected via WMI.*

[Screenshot Required: 08 Services]
*Figure 12.8: Live status of Windows services running on the endpoint.*

[Screenshot Required: 09 Live Console]
*Figure 12.9: The interactive WebSocket terminal connected to the remote VM.*

[Screenshot Required: 10 Commands]
*Figure 12.10: The remote command queue history and output logs.*

[Screenshot Required: 11 Alerts]
*Figure 12.11: System anomalies and security notifications.*

[Screenshot Required: 12 Users]
*Figure 12.12: System user management interface.*

[Screenshot Required: 13 Roles]
*Figure 12.13: RBAC roles and permissions configuration.*

[Screenshot Required: 14 Policies]
*Figure 12.14: Security and system policies interface.*

[Screenshot Required: 15 Groups]
*Figure 12.15: Endpoint grouping and organizational units interface.*

[Screenshot Required: 16 Settings]
*Figure 12.16: Global application settings.*

[Screenshot Required: 17 Installer]
*Figure 12.17: Custom Windows Agent Installation Wizard executing on the endpoint.*

[Screenshot Required: 18 Windows Service]
*Figure 12.18: The Windows Task Manager showing `SentinelAgentService` running smoothly in the background.*

[Screenshot Required: 19 Multiple VMs Online]
*Figure 12.19: Dashboard successfully tracking concurrent active Windows VMs.*

[Screenshot Required: 20 Database]
*Figure 12.20: Database interface showing populated telemetry tables.*
