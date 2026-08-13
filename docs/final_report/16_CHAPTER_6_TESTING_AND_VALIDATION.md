# CHAPTER 6: TESTING AND VALIDATION

## 6.1 Testing Methodology
The project utilized a test-driven approach for the backend and agent, heavily relying on pytest and pytest-asyncio for asynchronous unit and integration testing. Frontend components were validated through manual functional testing.

## 6.2 Backend Testing
Unit tests verified the Alert evaluation logic (e.g., ensuring consecutive heartbeat thresholds properly triggered state transitions) and the command execution state machine. API testing was conducted to ensure proper JWT validation and error handling.

## 6.3 Agent Testing
Agent tests mocked the HTTP transport (httpx.MockTransport) to simulate backend responses, verifying that the HeartbeatTask and HardwareInventoryTask correctly assembled payloads and handled offline caching. 

## 6.4 Deployment Testing
Deployment testing involved packaging the agent into a PyInstaller executable and deploying it on an isolated Windows VM. Network disconnects were simulated to ensure the agent's retry mechanisms functioned correctly.

## 6.5 Functional Testing (Test Cases)
[TEST EVIDENCE REQUIRED]
Detailed evidence of frontend rendering, database persistence, and WebSocket real-time delivery requires screenshots and log outputs mapped in the appendices.
