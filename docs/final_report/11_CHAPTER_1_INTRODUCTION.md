# CHAPTER 1: INTRODUCTION

## 1.1 Background
In the era of distributed workforces and sophisticated cyber threats, organizations require persistent, real-time visibility into their endpoint infrastructure. Traditional endpoint management solutions often suffer from high latency, rigid architectures, and poor integration capabilities. There is a pressing need for a lightweight, easily deployable agent that can stream telemetry—ranging from hardware health to security state—back to a centralized administrative console.

## 1.2 Problem Statement
Enterprise IT and Security teams lack a cohesive, centralized platform to monitor the performance, hardware state, and security posture of remote Windows endpoints in real time. Existing tools are frequently fragmented, requiring administrators to pivot between multiple dashboards to orchestrate commands, track memory anomalies, and verify security configurations like disk encryption.

## 1.3 Motivation
The motivation behind Endpoint Sentinel X is to build a unified monitoring and management ecosystem leveraging modern cloud-native architectures and asynchronous communication. By combining a low-footprint Python-based Windows agent with a highly concurrent FastAPI backend, the system aims to provide near-instantaneous telemetry and orchestration capabilities.

## 1.4 Objectives
- **Continuous Monitoring**: Collect hardware, OS, network, and software inventory data on configurable schedules.
- **Real-Time Telemetry & Alerting**: Stream performance metrics (CPU, memory) and generate automated alerts when thresholds are breached.
- **Command Orchestration**: Enable administrators to dispatch remote commands to endpoints and retrieve execution results securely.
- **Robust Security**: Secure endpoint-to-server communication using JWT authentication and localized identity encryption (DPAPI).

## 1.5 Scope
The scope of this project includes the development of a Windows-compatible endpoint agent, a RESTful and WebSocket-enabled backend, and a React-based administrative dashboard. The system is scoped to support Windows OS environments for the agent, with the backend deployed on the Render cloud platform.

## 1.6 Significance
Endpoint Sentinel X significantly reduces the mean time to detect (MTTD) hardware degradation and security policy violations (e.g., unencrypted drives). It serves as a foundational platform that can be extended with advanced automated remediation and threat intelligence integrations.

## 1.7 Project Overview
The project follows a standard software development lifecycle. Chapter 2 reviews existing literature and approaches. Chapter 3 outlines system requirements. Chapter 4 details the architectural design. Chapter 5 covers the technical implementation, followed by Testing in Chapter 6, Results in Chapter 7, and Conclusion in Chapter 8.
