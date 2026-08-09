# Endpoint Sentinel X
## Final Year Engineering Project Report

---

# Front Matter

## Title Page
**Project Title:** Endpoint Sentinel X: Design and Implementation of a Centralized Endpoint Monitoring and Remote Management Platform for Windows Systems
**Degree:** Bachelor of Technology
**Submitted By:** [Student Name & ID]
**Guided By:** [Guide Name]
**Institution:** Birla Institute of Technology & Science, Pilani (WILP)

## Certificate
This is to certify that the project work entitled **"Endpoint Sentinel X"** is a bonafide work carried out by [Student Name] in partial fulfillment for the award of the degree of [Degree Name] from BITS Pilani.

## Candidate Declaration
I hereby declare that this report, submitted in partial fulfillment of the requirements for the degree of [Degree Name], is a record of my original work under the guidance of [Guide Name].

## Acknowledgement
I would like to express my sincere gratitude to my project guide and BITS Pilani faculty for their continuous support and guidance throughout the development of Endpoint Sentinel X.

## Abstract
Modern enterprise IT environments require robust, real-time visibility and management of endpoint devices. **Endpoint Sentinel X** is designed to provide centralized remote management and telemetry specifically for Windows systems. The platform consists of a lightweight, highly privileged Windows Agent, a scalable asynchronous FastAPI backend leveraging PostgreSQL, and a modern React-based web dashboard. The objective of this project is to enable real-time hardware and software inventory collection, asynchronous remote command execution, and a WebSocket-driven "Live Console" that provides direct interactive shell access. 

The methodology followed an iterative, architecture-first approach, moving from backend schema design to agent telemetry collection and frontend visualization. Technologies utilized include Python, FastAPI, SQLAlchemy, React, and WebSockets. The system was successfully deployed and demonstrated the capability to provide real-time telemetry, secure enrollment, and a fully functional live console over a scalable architecture. The implemented prototype demonstrates the feasibility of centralized endpoint monitoring and remote management using modern asynchronous web technologies. The project validates the integration of Windows service-based agents, RESTful APIs, WebSockets, and a web-based management console within a unified architecture.

## Table of Contents
*(To be generated dynamically upon final assembly)*

## List of Acronyms & Abbreviations
*   **API:** Application Programming Interface
*   **EDR:** Endpoint Detection and Response
*   **JSON:** JavaScript Object Notation
*   **JWT:** JSON Web Token
*   **ORM:** Object-Relational Mapping
*   **REST:** Representational State Transfer
*   **SCM:** Service Control Manager (Windows)
*   **WMI:** Windows Management Instrumentation
*   **RBAC:** Role-Based Access Control

---

# Chapter 1. Introduction

## 1.1 Background
As organizational boundaries dissolve and remote work models become the standard, IT administrators face increasing challenges in monitoring and managing distributed fleets of Windows machines. The rapid shift toward hybrid work environments, accelerated cloud adoption, and ever-increasing endpoint counts have amplified the complexity of securing and maintaining corporate assets. Furthermore, the rising volume of cybersecurity threats necessitates constant visibility into endpoint health. Traditional management tools often rely on complex Active Directory domain bindings, VPNs, or legacy protocols like WinRM/RPC, which struggle to operate reliably over the public internet. There is a clear need for cloud-native, real-time endpoint management systems that operate securely over standard HTTPS/WebSocket connections. Endpoint Sentinel X was developed to address these challenges through a centralized architecture capable of securely collecting telemetry and supporting remote administrative operations over standard internet protocols.

## 1.2 Motivation
The primary motivation behind Endpoint Sentinel X is to bridge the gap between heavy, existing enterprise endpoint management solutions and the need for a streamlined, real-time administrative tool. By utilizing modern web technologies—specifically asynchronous Python (FastAPI), React, and WebSockets—administrators can gain immediate visibility into system health and execute remote commands without the traditional polling delays associated with legacy management platforms.

## 1.3 Problem Statement
Organizations require centralized visibility and secure remote administration of geographically distributed Windows endpoints while minimizing infrastructure complexity and administrative overhead. Existing solutions often lack the agility to perform real-time interactive diagnostics on off-network machines without relying on third-party remote desktop software or complex VPN routing.

## 1.4 Objectives
The core objectives of the Endpoint Sentinel X project are:
1.  **Real-Time Telemetry:** To build a Windows agent capable of extracting deep system metrics (CPU, Memory, Disks, Network, Windows Services, Software) via WMI and PSutil, transmitting it securely to a centralized database.
2.  **Remote Execution Engine:** To implement a robust, asynchronous command queuing system that allows administrators to dispatch PowerShell and Command Prompt (CMD) scripts to remote endpoints.
3.  **Interactive Live Console:** To engineer a low-latency communication channel over secure WebSockets, directly connecting the web browser to the endpoint's shell.
4.  **Secure Architecture:** To enforce strict Role-Based Access Control (RBAC), JWT authentication, and secure HTTPS/TLS communication for all telemetry and commands.

## 1.5 Scope
The current implementation of Endpoint Sentinel X is scoped exclusively to **Microsoft Windows** operating systems. The core functionalities included are:
*   Agent Enrollment
*   Endpoint Health Monitoring
*   Inventory Collection (Hardware, Software, Network, Services)
*   Live Console (Interactive Shell)
*   Remote Commands Execution
*   Global Web Dashboard
*   Authentication & RBAC
*   Windows Service Lifecycle Management

## 1.6 Limitations
Based on the current source code implementation:
*   The platform only supports Windows endpoints. macOS and Linux agents are not implemented.
*   The system requires endpoints to have outbound internet access to reach the centralized API; there is no peer-to-peer relay capability.
*   While an alerts framework exists, advanced AI-based anomaly detection or SIEM integration is out of scope.
*   The current implementation is intended for educational and prototype enterprise environments and has not been evaluated under large-scale production deployments.

## 1.7 Contributions
*   Developed a custom, compiled Windows executable agent using PyInstaller that runs as a Windows service running under the LocalSystem account.
*   Designed and implemented an asynchronous backend using FastAPI, SQLAlchemy 2.0, and PostgreSQL to support endpoint enrollment, inventory synchronization, remote command processing, and live communication.
*   Developed a React and TypeScript based web management console utilizing a modular component architecture.

## 1.8 Report Organization
The remainder of this report is organized as follows:
*   **Chapter 2** covers the Literature Review.
*   **Chapter 3 & 4** detail the System and Requirement Analysis.
*   **Chapter 5 & 6** explore the System Architecture and Database Design.
*   **Chapter 7 & 8** provide UML Modeling and Core Workflows.
*   **Chapter 9 & 10** document the APIs and Implementation details.
*   **Chapter 11** discusses Testing and Results.
*   **Chapter 12** concludes the report and discusses future scope.

## 1.9 Methodology
The project followed an iterative Agile-inspired development methodology. The implementation was completed through incremental development phases beginning with backend infrastructure, followed by agent development, frontend implementation, testing, debugging, and system integration. Each phase concluded with verification before proceeding to the next milestone.

## 1.10 Technologies Used

| Layer | Technology |
| :--- | :--- |
| **Backend** | FastAPI, Uvicorn |
| **Database** | PostgreSQL |
| **ORM** | SQLAlchemy 2.0 |
| **Database Migration** | Alembic |
| **Agent** | Python |
| **Frontend** | React + TypeScript + Vite |
| **Styling** | Tailwind CSS |
| **Authentication** | JWT |
| **Communication**| REST API, WebSockets |
| **Packaging** | PyInstaller |

## 1.11 Development Environment

| Component | Specification |
| :--- | :--- |
| **Operating System** | Windows 11 |
| **IDE** | Visual Studio Code |
| **Language** | Python 3.13 |
| **Database** | PostgreSQL (Neon) |
| **Browser** | Google Chrome |
| **Version Control** | Git & GitHub |
| **Virtualization** | Hyper-V |
| **API Testing** | Swagger UI |
