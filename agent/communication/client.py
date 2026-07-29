import time
import uuid
import random
import asyncio
import logging
import httpx
from typing import Any, Dict, Optional
from agent.utils.storage import StorageProvider

logger = logging.getLogger(__name__)

class AgentHTTPClient:
    """Robust, asynchronous HTTP transport client wrapping HTTPX with tracing, DPAPI token checks, and auto-refresh."""

    def __init__(
        self,
        base_url: str,
        storage: Optional[StorageProvider] = None,
        timeout_seconds: int = 10,
        max_retries: int = 3,
        verify_tls: bool = True
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.storage = storage
        self.timeout = httpx.Timeout(timeout_seconds)
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            verify=verify_tls,
            follow_redirects=True
        )
        self.default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    async def close(self) -> None:
        """Gracefully release client connection pools."""
        await self.client.aclose()

    async def _rotate_tokens(self) -> bool:
        """Invokes the backend refresh route using the opaque refresh token and caches new tokens."""
        if not self.storage:
            return False

        tokens_data = await self.storage.read("tokens")
        if not tokens_data or not tokens_data.get("refresh_token"):
            logger.error("No refresh token stored. Cannot rotate session.")
            return False

        refresh_token = tokens_data["refresh_token"]

        try:
            # Direct POST to auth/refresh bypasses auth header checks
            req_headers = self.default_headers.copy()
            req_id = str(uuid.uuid4())
            req_headers["X-Request-ID"] = req_id
            req_headers["X-Correlation-ID"] = req_id

            req = self.client.build_request(
                method="POST",
                url="/auth/refresh",
                json={"refresh_token": refresh_token},
                headers=req_headers
            )
            resp = await self.client.send(req)

            if resp.status_code != 200:
                logger.error(f"Session token rotation failed with status: {resp.status_code}")
                # Clear invalid tokens to trigger re-enrollment flow on subsequent calls
                await self.storage.delete("tokens")
                return False

            res_json = resp.json()
            if not res_json.get("success"):
                logger.error(f"Rotation rejected: {res_json.get('message')}")
                await self.storage.delete("tokens")
                return False

            data = res_json.get("data", {})
            new_access = data.get("access_token")
            new_refresh = data.get("refresh_token")

            if not new_access or not new_refresh:
                logger.error("Session rotation response missing credentials.")
                return False

            # Persist new token pair to secure storage
            await self.storage.write("tokens", {
                "access_token": new_access,
                "refresh_token": new_refresh
            })
            logger.info("Session access and refresh tokens rotated successfully.")
            return True

        except Exception as e:
            logger.exception(f"Exception during session token rotation: {e}")
            return False

    async def request(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        auth_token: Optional[str] = None
    ) -> httpx.Response:
        """Sends HTTP request with full trace logs, correlation IDs, and automated JWT token management."""
        url_path = f"/{path.lstrip('/')}"
        
        req_headers = self.default_headers.copy()
        if headers:
            req_headers.update(headers)
            
        # 1. Resolve Auth Token from secure storage if not supplied
        resolved_token = auth_token
        if not resolved_token and self.storage:
            tokens_data = await self.storage.read("tokens")
            if tokens_data:
                resolved_token = tokens_data.get("access_token")

        if resolved_token:
            req_headers["Authorization"] = f"Bearer {resolved_token}"

        # Generate unique request and correlation IDs for distributed tracing
        req_id = str(uuid.uuid4())
        corr_id = req_headers.get("X-Correlation-ID") or str(uuid.uuid4())
        req_headers["X-Request-ID"] = req_id
        req_headers["X-Correlation-ID"] = corr_id

        attempt = 0
        backoff_factor = 1.0  # Base scale in seconds

        while True:
            attempt += 1
            start_time = time.perf_counter()
            
            logger.info(
                f"HTTP outbound request: {method} {url_path} | Attempt: {attempt} | ReqID: {req_id}",
                extra={"request_id": req_id, "correlation_id": corr_id}
            )

            try:
                req = self.client.build_request(
                    method=method,
                    url=url_path,
                    json=json_data,
                    headers=req_headers
                )
                resp = await self.client.send(req)
                duration = time.perf_counter() - start_time
                
                logger.info(
                    f"HTTP response received | Status: {resp.status_code} | Duration: {duration:.4f}s | ReqID: {req_id}",
                    extra={"request_id": req_id, "correlation_id": corr_id}
                )

                # 2. Transparent JWT Access Token Expiry Handling (401 Unauthorized)
                if resp.status_code == 401 and self.storage and not auth_token:
                    logger.warning("Access token rejected (401). Attempting automatic refresh...")
                    refreshed = await self._rotate_tokens()
                    if refreshed:
                        tokens_data = await self.storage.read("tokens")
                        if tokens_data and tokens_data.get("access_token"):
                            req_headers["Authorization"] = f"Bearer {tokens_data['access_token']}"
                            # Re-send the request with new token
                            req = self.client.build_request(
                                method=method,
                                url=url_path,
                                json=json_data,
                                headers=req_headers
                            )
                            resp = await self.client.send(req)
                            duration = time.perf_counter() - start_time
                            logger.info(
                                f"HTTP response received after token refresh | Status: {resp.status_code} | Duration: {duration:.4f}s | ReqID: {req_id}",
                                extra={"request_id": req_id, "correlation_id": corr_id}
                            )
                            return resp

                # Retry on server errors (5xx)
                if resp.status_code >= 500 and attempt < self.max_retries:
                    raise httpx.HTTPStatusError(
                        f"Server error status {resp.status_code}",
                        request=req,
                        response=resp
                    )
                return resp

            except (httpx.HTTPError, OSError) as e:
                duration = time.perf_counter() - start_time
                logger.warning(
                    f"HTTP call failed | Attempt: {attempt} | Duration: {duration:.4f}s | Error: {e} | ReqID: {req_id}",
                    extra={"request_id": req_id, "correlation_id": corr_id}
                )

                if attempt >= self.max_retries:
                    raise e

                # Full Jitter backoff logic: sleep = random(0, base * 2^attempt)
                max_sleep = backoff_factor * (2 ** (attempt - 1))
                sleep_duration = random.uniform(0.1, max_sleep)
                
                logger.info(
                    f"Retrying request in {sleep_duration:.2f}s | ReqID: {req_id}",
                    extra={"request_id": req_id, "correlation_id": corr_id}
                )
                await asyncio.sleep(sleep_duration)
