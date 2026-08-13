# CHAPTER 7: RESULTS AND DISCUSSION

## 7.1 System Results
The finalized Endpoint Sentinel X platform successfully met all core objectives outlined in Chapter 1. The agent reliably authenticated and transmitted inventory data, visible immediately within the centralized dashboard.

## 7.2 Dashboard and Inventory
The React frontend accurately rendered connected endpoints, distinguishing online/offline status based on recent heartbeat timestamps. Detailed views successfully populated hardware, OS, and software lists derived from WMI.

## 7.3 Performance and Alerts
The system successfully detected simulated memory spikes on the Windows VM, triggering HIGH_MEMORY alerts. The duplicate prevention logic held, ensuring only one active alert existed per endpoint. Upon memory reduction, the alert was correctly marked as resolved.

## 7.4 Command Orchestration
Remote command execution operated with low latency. Output from commands like lush_dns was accurately captured and presented in the frontend terminal UI.

## 7.5 Discussion of Results
The Hexagonal architecture proved highly beneficial during testing, as core logic (alert evaluation) could be tested entirely independent of the database or HTTP layer. The DPAPI implementation successfully bound agent identity to the physical machine, thwarting unauthorized copying of credentials.
