# Chapter 2. Literature Review

## 2.1 Overview
The management and monitoring of endpoint devices have evolved significantly over the past two decades. As organizations transition from perimeter-based security models to zero-trust architectures, the need for robust endpoint visibility has given rise to sophisticated Endpoint Detection and Response (EDR) and Unified Endpoint Management (UEM) solutions. This chapter reviews the current state of endpoint management by analyzing prominent commercial and open-source platforms. By comparing these existing systems, we contextualize the architectural decisions and unique value proposition of Endpoint Sentinel X.

## 2.2 Existing Endpoint Management Solutions

### 2.2.1 Microsoft Intune
Microsoft Intune is a cloud-based unified endpoint management service that focuses on mobile device management (MDM) and mobile application management (MAM). 
*   **Advantages:** Deep integration with Azure Active Directory (Entra ID) and Windows Autopilot, allowing for seamless provisioning and policy enforcement across large enterprises.
*   **Limitations:** Intune is primarily designed for asynchronous policy deployment rather than real-time interactive diagnostics. It does not provide an instant, low-latency interactive shell (like a live console) for immediate troubleshooting.

### 2.2.2 Microsoft Defender for Endpoint
Microsoft Defender for Endpoint is a comprehensive enterprise endpoint security platform designed to prevent, detect, investigate, and respond to advanced threats.
*   **Advantages:** Offers unparalleled threat intelligence and deep OS-level integration for behavioral monitoring.
*   **Limitations:** It is an incredibly heavy and complex system requiring significant licensing costs and specialized security operations center (SOC) expertise to operate effectively. It focuses heavily on security response rather than general IT administrative telemetry.

### 2.2.3 CrowdStrike Falcon
CrowdStrike Falcon is a leading cloud-delivered endpoint protection platform utilizing a single lightweight agent architecture.
*   **Advantages:** Excellent at real-time threat hunting and automated remediation using AI. The single-agent design minimizes endpoint resource consumption.
*   **Limitations:** Highly commercialized with significant deployment costs. The platform's proprietary nature makes it difficult for organizations to extend or customize the telemetry collection pipelines for specific, non-security-related administrative needs.

### 2.2.4 ManageEngine Endpoint Central
ManageEngine Endpoint Central (formerly Desktop Central) is a comprehensive UEM solution that helps in managing servers, laptops, desktops, smartphones, and tablets from a central location.
*   **Advantages:** Offers a wide array of IT management features including patch management, software deployment, and traditional remote desktop control.
*   **Limitations:** The architecture is traditionally on-premise heavy, often requiring VPNs for off-network management. Its remote control features rely on traditional screen-scraping/VNC protocols rather than lightweight, headless WebSocket terminals.

### 2.2.5 Wazuh
Wazuh is a free, open-source security monitoring platform that collects, aggregates, and analyzes endpoint security data.
*   **Advantages:** Open-source, highly extensible, and offers strong integration with the ELK (Elasticsearch, Logstash, Kibana) stack for SIEM capabilities.
*   **Limitations:** Wazuh is fundamentally a log collection and HIDS (Host-based Intrusion Detection System). It is not designed for real-time remote administrative commands or interactive shell execution.

### 2.2.6 OpenEDR
OpenEDR is an open-source endpoint detection and response platform that provides visibility into endpoint activity.
*   **Advantages:** Free access to advanced EDR capabilities and deep process monitoring.
*   **Limitations:** The platform suffers from a steep learning curve, complex infrastructure requirements for data storage, and lacks a modern, low-latency web console dedicated to general IT operations and interactive diagnostics.

## 2.3 Comparative Analysis

The following table summarizes the comparison between Endpoint Sentinel X and the reviewed existing systems across key functional areas required by modern IT administrators.

| Feature / Platform | Real-Time Telemetry | Interactive Live Shell (WebSocket) | Asynchronous Command Queuing | Open Source / Custom Architecture | Target Focus |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Microsoft Intune** | Delayed / Polled | No | Yes (Scripts) | No | Unified Endpoint Mgmt |
| **Microsoft Defender** | Real-Time | Yes (Live Response) | No | No | Threat Detection (EDR) |
| **CrowdStrike Falcon**| Real-Time | Yes (Real Time Response)| No | No | Threat Detection (EDR) |
| **Endpoint Central** | Polled | No (Uses VNC/RDP) | Yes | No | Traditional IT Mgmt |
| **Wazuh** | Near Real-Time | No | No | Yes | SIEM / HIDS |
| **OpenEDR** | Real-Time | No | No | Yes | Open Source EDR |
| **Endpoint Sentinel X**| **Real-Time** | **Yes (Low-Latency)** | **Yes** | **Yes (Prototype)** | **IT Mgmt & Diagnostics**|

## 2.4 Advantages of Endpoint Sentinel X

Based on the literature review, Endpoint Sentinel X introduces several architectural advantages for specific use cases:
1.  **Lightweight Infrastructure:** By leveraging Python, FastAPI, and PostgreSQL, the backend avoids the heavy infrastructure requirements of platforms like Wazuh or CrowdStrike.
2.  **Interactive Diagnostics:** Unlike Intune or Endpoint Central, Sentinel X implements a direct WebSocket-driven Live Console, allowing administrators to execute commands instantly without requiring full GUI remote desktop sessions.
3.  **Modern Cloud-Native Stack:** The use of React, WebSockets, and asynchronous Python ensures that the platform can manage off-network endpoints natively over standard HTTPS (Port 443), eliminating the need for complex VPN configurations.

## 2.5 Limitations of Endpoint Sentinel X
While providing a streamlined diagnostic experience, the current prototype of Endpoint Sentinel X lacks the advanced malware detection heuristics, patch management, and automated remediation capabilities found in mature platforms like CrowdStrike Falcon or Microsoft Defender. Additionally, it is currently limited to the Windows operating system.
