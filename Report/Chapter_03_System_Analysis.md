# Chapter 3. System Analysis

## 3.1 Introduction
System analysis is the process of studying a procedure or business in order to identify its goals and purposes and create systems and procedures that will achieve them in an efficient way. This chapter analyzes the existing methodologies for endpoint management, identifies their core problems, and presents the proposed Endpoint Sentinel X system as a viable, modern alternative. 

## 3.2 Existing System
Traditionally, organizations manage Windows endpoints using a combination of Active Directory Group Policies (GPO), Systems Center Configuration Manager (SCCM), or legacy remote management tools relying on protocols such as Windows Management Instrumentation (WMI) over DCOM, Remote Desktop Protocol (RDP), and PowerShell Remoting (WinRM). 

These systems typically operate on a pull-based polling mechanism where the centralized server queries endpoints on a fixed schedule, or clients check in periodically to download policies and upload inventory data. 

## 3.3 Problems in Existing System
The legacy systems exhibit several significant drawbacks in modern, geographically distributed IT environments:
1.  **Network Boundary Limitations:** Traditional protocols (DCOM, RPC, WinRM) require complex firewall configurations and are generally blocked over the public internet, necessitating costly and complex VPN infrastructure for remote workers.
2.  **High Latency:** Scheduled polling mechanisms mean that telemetry data is often stale. Security alerts or system state changes may not be visible to administrators until the next polling cycle.
3.  **Heavy Infrastructure:** Solutions like SCCM require substantial on-premise infrastructure, database servers, and distribution points, leading to high operational overhead.
4.  **Lack of Interactive Diagnostics:** While tools can push scripts, they rarely offer a real-time, bidirectional interactive shell without falling back to heavy GUI-based remote desktop software, which consumes significant bandwidth and invades user privacy.

## 3.4 Proposed System
Endpoint Sentinel X is proposed as a cloud-native, asynchronous endpoint management platform. It replaces heavy polling architectures with a lightweight, push-based telemetry model and real-time WebSocket communication. The system utilizes a compiled Python agent running as a Windows Service, communicating over standard HTTPS (Port 443) to a centralized FastAPI backend.

## 3.5 Advantages of Proposed System
1.  **Real-Time Telemetry:** The agent pushes inventory and heartbeat data instantly upon changes or service startup, ensuring the central dashboard reflects near real-time asset states.
2.  **NAT and Firewall Traversal:** By utilizing outbound HTTPS and secure WebSockets, the agent can connect to the management server from any internet-connected network without requiring VPNs or inbound firewall rules.
3.  **Low Latency Execution:** The Live Console feature provides an interactive shell experience with sub-second latency, enabling administrators to diagnose issues as if they were sitting at the machine.
4.  **Scalability:** The asynchronous nature of the FastAPI backend and asyncpg PostgreSQL driver allows a single management server to handle thousands of concurrent WebSocket connections efficiently.

## 3.6 Assumptions and Constraints
### 3.6.1 Assumptions
*   Endpoints have reliable outbound internet access on TCP Port 443.
*   The deployment environment allows the installation of third-party Windows Services.
*   Administrators accessing the web console are using modern, WebSocket-compatible web browsers.

### 3.6.2 Constraints
*   **Operating System Dependency:** The agent relies heavily on Windows-specific APIs (WMI, Windows Registry, Windows Service Control Manager). It cannot be deployed on macOS or Linux platforms.
*   **Privilege Requirement:** The agent must be installed and run under the `LocalSystem` account (NT AUTHORITY\SYSTEM) to collect comprehensive hardware data and execute administrative scripts.
*   **Data Retention:** As telemetry data scales, the centralized PostgreSQL database will require aggressive partitioning or archiving strategies to maintain performance, which is not fully implemented in the current prototype.
