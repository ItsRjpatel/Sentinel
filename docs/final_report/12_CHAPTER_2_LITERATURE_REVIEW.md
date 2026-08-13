# CHAPTER 2: LITERATURE REVIEW

## 2.1 Existing Endpoint Management Approaches
Enterprise endpoint management has evolved from simple asset tracking to complex Remote Monitoring and Management (RMM) and Endpoint Detection and Response (EDR) solutions. Tools like Microsoft Endpoint Manager (Intune), CrowdStrike, and open-source alternatives like OSquery provide extensive capabilities. 

## 2.2 Existing Limitations
Many commercial solutions are heavy on endpoint resources, require complex on-premises infrastructure, or operate with significant polling latency. Open-source solutions like OSquery are powerful for querying state but lack built-in real-time alerting and remote command orchestration tailored for instantaneous administrative response.

## 2.3 Relevant Technologies and Concepts
- **Asynchronous I/O**: Essential for handling thousands of concurrent endpoint connections efficiently.
- **WebSocket Protocol**: Enables full-duplex communication, crucial for real-time telemetry streaming and command execution.
- **Hexagonal Architecture**: Promotes the separation of core business logic from external frameworks, improving testability and maintainability.

## 2.4 Comparison with Existing Approaches
Unlike traditional RMMs that rely on heavy polling intervals (e.g., 15-30 minutes), Endpoint Sentinel X utilizes a persistent heartbeat combined with WebSockets. This allows for sub-second telemetry delivery and immediate command dispatch, bridging the gap between monitoring and active management.

## 2.5 Research and Technical Gap
There is a technical gap in accessible, easily extensible, real-time monitoring solutions built purely on modern web stacks (Python FastAPI and React) that can be easily customized by internal development teams without vendor lock-in.

## 2.6 How Endpoint Sentinel X Addresses the Gap
Endpoint Sentinel X addresses these gaps by providing an open, modular architecture. The use of a Python-based agent allows for rapid addition of new telemetry collectors, while the FastAPI backend provides a standardized REST API that can be easily integrated into broader enterprise workflows.
