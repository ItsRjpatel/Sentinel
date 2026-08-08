import json
import logging
import os
import platform
import shutil
import socket
import subprocess
import sys
import tkinter as tk
import urllib.parse
import urllib.request
from tkinter import messagebox

import asyncio
from pathlib import Path
from agent.security.identity import get_hardware_identifiers, load_or_create_identity
from agent.utils.storage import DPAPIJSONStorageProvider


class SentinelEnrollmentWizard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Endpoint Sentinel X – Agent Enrollment Wizard")
        self.root.geometry("540x560")
        self.root.resizable(False, False)
        self.root.configure(bg="#0d1117")

        # Set default values
        self.default_hostname = socket.gethostname()
        self.server_url_var = tk.StringVar(value="http://127.0.0.1:8000")
        self.token_var = tk.StringVar(value="sentinel-secret-key-change-in-production")
        self.department_var = tk.StringVar(value="IT Operations")
        self.hostname_var = tk.StringVar(value=self.default_hostname)
        self.agent_name_var = tk.StringVar(value=f"{self.default_hostname}-Agent")

        self.status_var = tk.StringVar(value="Not Tested")
        self.status_color = "#8b949e"

        # Detect Upgrade vs Fresh Install
        prog_data = os.environ.get("PROGRAMDATA", "C:\\ProgramData")
        identity_file = os.path.join(prog_data, "EndpointSentinel", "identity.json")
        self.is_upgrade = os.path.exists(identity_file)

        self._build_ui()

    def _build_ui(self):
        # Header banner
        header_frame = tk.Frame(self.root, bg="#161b22", pady=15, padx=20)
        header_frame.pack(fill="x")

        title_label = tk.Label(
            header_frame,
            text="Endpoint Sentinel X Agent",
            font=("Segoe UI", 14, "bold"),
            fg="#58a6ff",
            bg="#161b22",
        )
        title_label.pack(anchor="w")

        subtitle_text = "Enterprise Endpoint Enrollment & Management Setup"
        if self.is_upgrade:
            subtitle_text = "Enterprise Endpoint Enrollment (Upgrade Mode)"

        subtitle_label = tk.Label(
            header_frame,
            text=subtitle_text,
            font=("Segoe UI", 9),
            fg="#8b949e",
            bg="#161b22",
        )
        subtitle_label.pack(anchor="w")

        # Main Body Form
        form_frame = tk.Frame(self.root, bg="#0d1117", padx=25, pady=15)
        form_frame.pack(fill="both", expand=True)

        # 1. Management Server URL
        tk.Label(
            form_frame,
            text="Management Server URL",
            font=("Segoe UI", 9, "bold"),
            fg="#c9d1d9",
            bg="#0d1117",
        ).pack(anchor="w", pady=(5, 2))
        url_entry = tk.Entry(
            form_frame,
            textvariable=self.server_url_var,
            font=("Consolas", 10),
            bg="#21262d",
            fg="#c9d1d9",
            insertbackground="#c9d1d9",
            bd=1,
            relief="solid",
        )
        url_entry.pack(fill="x", ipady=4)

        # 2. Enrollment Token
        tk.Label(
            form_frame,
            text="Enrollment Token / Secret",
            font=("Segoe UI", 9, "bold"),
            fg="#c9d1d9",
            bg="#0d1117",
        ).pack(anchor="w", pady=(10, 2))
        token_entry = tk.Entry(
            form_frame,
            textvariable=self.token_var,
            font=("Consolas", 10),
            bg="#21262d",
            fg="#c9d1d9",
            insertbackground="#c9d1d9",
            bd=1,
            relief="solid",
        )
        token_entry.pack(fill="x", ipady=4)

        # 3. Department
        tk.Label(
            form_frame,
            text="Department / Group Tag",
            font=("Segoe UI", 9, "bold"),
            fg="#c9d1d9",
            bg="#0d1117",
        ).pack(anchor="w", pady=(10, 2))
        dept_entry = tk.Entry(
            form_frame,
            textvariable=self.department_var,
            font=("Segoe UI", 9),
            bg="#21262d",
            fg="#c9d1d9",
            insertbackground="#c9d1d9",
            bd=1,
            relief="solid",
        )
        dept_entry.pack(fill="x", ipady=4)

        # 4. Hostname & Agent Name
        grid_frame = tk.Frame(form_frame, bg="#0d1117")
        grid_frame.pack(fill="x", pady=(10, 5))

        left_col = tk.Frame(grid_frame, bg="#0d1117")
        left_col.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Label(
            left_col,
            text="Endpoint Hostname",
            font=("Segoe UI", 9, "bold"),
            fg="#c9d1d9",
            bg="#0d1117",
        ).pack(anchor="w", pady=(0, 2))
        host_entry = tk.Entry(
            left_col,
            textvariable=self.hostname_var,
            font=("Consolas", 9),
            bg="#21262d",
            fg="#c9d1d9",
            insertbackground="#c9d1d9",
            bd=1,
            relief="solid",
        )
        host_entry.pack(fill="x", ipady=4)

        right_col = tk.Frame(grid_frame, bg="#0d1117")
        right_col.pack(side="right", fill="x", expand=True, padx=(5, 0))
        tk.Label(
            right_col,
            text="Agent Display Name",
            font=("Segoe UI", 9, "bold"),
            fg="#c9d1d9",
            bg="#0d1117",
        ).pack(anchor="w", pady=(0, 2))
        agent_entry = tk.Entry(
            right_col,
            textvariable=self.agent_name_var,
            font=("Segoe UI", 9),
            bg="#21262d",
            fg="#c9d1d9",
            insertbackground="#c9d1d9",
            bd=1,
            relief="solid",
        )
        agent_entry.pack(fill="x", ipady=4)

        # 5. Pre-Enrollment Connectivity Test Box
        test_frame = tk.Frame(
            form_frame, bg="#161b22", bd=1, relief="solid", pady=8, padx=12
        )
        test_frame.pack(fill="x", pady=(15, 10))

        test_top = tk.Frame(test_frame, bg="#161b22")
        test_top.pack(fill="x")

        tk.Label(
            test_top,
            text="Server Connectivity Test:",
            font=("Segoe UI", 9, "bold"),
            fg="#c9d1d9",
            bg="#161b22",
        ).pack(side="left")
        self.status_label = tk.Label(
            test_top,
            textvariable=self.status_var,
            font=("Segoe UI", 9, "bold"),
            fg="#8b949e",
            bg="#161b22",
        )
        self.status_label.pack(side="right")

        test_btn = tk.Button(
            test_frame,
            text="Test Connection (Ping / REST API / WebSocket)",
            font=("Segoe UI", 8, "bold"),
            bg="#21262d",
            fg="#58a6ff",
            activebackground="#30363d",
            activeforeground="#58a6ff",
            bd=0,
            cursor="hand2",
            command=self.run_connectivity_test,
        )
        test_btn.pack(fill="x", pady=(6, 0))

        # Footer Action Buttons
        footer_frame = tk.Frame(self.root, bg="#161b22", pady=12, padx=20)
        footer_frame.pack(fill="x", side="bottom")

        cancel_btn = tk.Button(
            footer_frame,
            text="Cancel",
            font=("Segoe UI", 9, "bold"),
            bg="#21262d",
            fg="#c9d1d9",
            activebackground="#30363d",
            activeforeground="#c9d1d9",
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2",
            command=self.root.destroy,
        )
        cancel_btn.pack(side="left")

        enroll_btn = tk.Button(
            footer_frame,
            text="Upgrade & Restart Agent" if self.is_upgrade else "Enroll & Start Agent Service",
            font=("Segoe UI", 9, "bold"),
            bg="#238636",
            fg="#ffffff",
            activebackground="#2ea043",
            activeforeground="#ffffff",
            bd=0,
            padx=20,
            pady=5,
            cursor="hand2",
            command=self.execute_enrollment,
        )
        enroll_btn.pack(side="right")

    def run_connectivity_test(self):
        """Tests REST API health and socket reachability to target server URL."""
        import logging

        logger = logging.getLogger("agent.wizard")

        raw_url = self.server_url_var.get().strip().rstrip("/")
        if not raw_url:
            messagebox.showwarning(
                "Warning", "Please enter a valid Management Server URL."
            )
            return

        # Normalize URL: ensure it uses /api/v1 as the base API path
        server_base = raw_url
        if server_base.endswith("/api/v1"):
            api_base = server_base
        else:
            api_base = f"{server_base}/api/v1"

        self.status_var.set("Testing...")
        self.status_label.configure(fg="#e3b341")
        self.root.update()

        candidate_urls = [
            f"{api_base}/openapi.json",
        ]

        last_error = None
        for health_url in candidate_urls:
            print(f"[WIZARD TEST] Requesting URL: {health_url}")
            logger.info(f"Testing connectivity to URL: {health_url}")

            try:
                # Bypass system proxy to prevent timeout issues on localhost/internal network
                proxy_handler = urllib.request.ProxyHandler({})
                opener = urllib.request.build_opener(proxy_handler)
                
                req = urllib.request.Request(
                    health_url, headers={"User-Agent": "SentinelAgentInstaller/0.9.0"}
                )
                with opener.open(req, timeout=30) as response:
                    status_code = response.status
                    body = response.read().decode("utf-8")
                    print(
                        f"[WIZARD TEST] URL: {health_url} -> Status: {status_code}, Body: {body[:150]}"
                    )
                    logger.info(
                        f"Health response from {health_url}: Status {status_code}"
                    )

                    if status_code in (200, 201):
                        try:
                            data = json.loads(body)
                            if "openapi" in data and "info" in data:
                                title = data["info"].get("title", "Unknown")
                                self.status_var.set(f"CONNECTED ({title})")
                                self.status_label.configure(fg="#3fb950")  # Green
                                return
                            else:
                                raise ValueError("Invalid OpenAPI schema structure.")
                        except json.JSONDecodeError:
                            raise ValueError("Response was not valid JSON.")
            except Exception as e:
                import traceback

                last_error = e
                err_trace = traceback.format_exc()
                print(f"[WIZARD TEST] Exception requesting {health_url}:\n{err_trace}")
                logger.warning(f"Failed reachability check for {health_url}: {e}")
                
                # Temporary UI logging for diagnostics
                messagebox.showerror(
                    "Connectivity Diagnostic Log",
                    f"URL: {health_url}\n"
                    f"Method: GET\n"
                    f"Timeout: 30s\n"
                    f"Exception:\n{err_trace}"
                )

        self.status_var.set(f"FAILED: {last_error}")
        self.status_label.configure(fg="#f85149")

    def execute_enrollment(self):
        """Executes API enrollment and installs Windows Service."""
        server_url = self.server_url_var.get().strip().rstrip("/")
        token = self.token_var.get().strip()
        department = self.department_var.get().strip()
        hostname = self.hostname_var.get().strip()

        if not server_url or not token:
            messagebox.showerror(
                "Error", "Server URL and Enrollment Token are required."
            )
            return

        try:
            # Prepare registration POST
            server_base = server_url
            if server_base.endswith("/api/v1"):
                api_base = server_base
            else:
                api_base = f"{server_base}/api/v1"
                
            enroll_url = f"{api_base}/endpoints/enroll"

            # Identity Preservation / Upgrade Check
            prog_data = os.environ.get("PROGRAMDATA", "C:\\ProgramData")
            agent_dir = os.path.join(prog_data, "EndpointSentinel")
            os.makedirs(agent_dir, exist_ok=True)
            
            storage_provider = DPAPIJSONStorageProvider(Path(agent_dir))
            identity = asyncio.run(load_or_create_identity(storage_provider))
            
            ids = get_hardware_identifiers()
            payload = {
                "hostname": hostname,
                "os_version": f"{platform.system()} {platform.release()}",
                "agent_id": identity.agent_uuid,
                "identity_version": getattr(identity, "identity_version", 1),
                "hardware_hash": identity.machine_fingerprint,
                "mac_addresses": [ids["mac_address"]] if ids.get("mac_address") else [],
                "ip_addresses": [socket.gethostbyname(hostname)]
                if hostname
                else ["127.0.0.1"],
            }

            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                enroll_url,
                data=req_data,
                headers={
                    "Content-Type": "application/json",
                    "X-Enrollment-Secret": token,
                },
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=30) as resp:
                res_body = json.loads(resp.read().decode("utf-8"))

            if not res_body.get("success"):
                raise RuntimeError(
                    res_body.get("message", "Enrollment rejected by server")
                )

            data = res_body.get("data", {})
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token", "")

            # Persist configuration to ProgramData selectively
            cfg_file = os.path.join(agent_dir, "config.json")
            config_data = {}
            if os.path.exists(cfg_file):
                try:
                    with open(cfg_file, "r", encoding="utf-8") as f:
                        config_data = json.load(f)
                except Exception as e:
                    logging.warning(f"Failed to read existing config.json: {e}")

            config_data.update({
                "server_url": server_url,
                "enrollment_secret": token,
                "department": department,
                "installed_at": platform.node(),
            })

            with open(cfg_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
                
            # Also save tokens to DPAPI (handled correctly now)
            tokens = {
                "access_token": access_token,
                "refresh_token": refresh_token
            }
            asyncio.run(storage_provider.write("tokens", tokens))

            # Deploy agent files and install Windows Service
            if os.name == "nt":
                install_dir = os.path.join(
                    os.environ.get("ProgramFiles", "C:\\Program Files"),
                    "Endpoint Sentinel",
                )
                
                if self.is_upgrade:
                    import time
                    import csv
                    import io
                    # Stop existing service to release file locks before deploying new executable
                    subprocess.run(["sc.exe", "stop", "SentinelAgent"], capture_output=True)
                    
                    # Poll SCM until the service is fully STOPPED (timeout after 15 seconds)
                    for _ in range(30):
                        res = subprocess.run(["sc.exe", "query", "SentinelAgent"], capture_output=True, text=True)
                        if "STOPPED" in res.stdout or "does not exist" in res.stdout:
                            break
                        time.sleep(0.5)
                        
                    # Wait for all processes to exit to release file locks (timeout after 15 seconds)
                    remaining_pids = []
                    for _ in range(30):
                        remaining_pids = []
                        res = subprocess.run(
                            ["tasklist", "/FI", "IMAGENAME eq SentinelAgentService.exe", "/FO", "CSV", "/NH"],
                            capture_output=True, text=True
                        )
                        output = res.stdout.strip()
                        if "INFO: No tasks" in output or not output:
                            break
                        
                        try:
                            reader = csv.reader(io.StringIO(output))
                            for row in reader:
                                if len(row) > 1 and "SentinelAgentService.exe" in row[0]:
                                    remaining_pids.append(row[1])
                        except Exception:
                            pass
                            
                        if not remaining_pids:
                            break
                        time.sleep(0.5)
                        
                    if remaining_pids:
                        raise RuntimeError(
                            f"Cannot upgrade agent. The following SentinelAgentService.exe processes failed to terminate: {', '.join(remaining_pids)}. "
                            "Please terminate them manually before trying again."
                        )
                
                self._deploy_agent_files(install_dir, agent_dir)

                if not self.is_upgrade:
                    svc_exe = os.path.join(install_dir, "SentinelAgentService.exe")
                    subprocess.run(
                        [
                            "sc.exe", "create", "SentinelAgent", "binPath=", f'"{svc_exe}" run',
                            "start=", "auto", "DisplayName=", "Endpoint Sentinel Agent",
                        ],
                        check=True,
                    )
                    subprocess.run(
                        [
                            "sc.exe", "failure", "SentinelAgent", "reset=", "86400",
                            "actions=", "restart/60000/restart/120000/restart/300000",
                        ],
                        check=True,
                    )
                
                subprocess.run(["sc.exe", "start", "SentinelAgent"], check=True)

            success_title = "Upgrade Success" if self.is_upgrade else "Enrollment Success"
            success_msg = f"Successfully upgraded agent and re-registered with Sentinel X Management Console!\n\nAssigned Agent ID: {identity.agent_uuid}" if self.is_upgrade else f"Successfully enrolled agent into Sentinel X Management Console!\n\nAssigned Agent ID: {identity.agent_uuid}"
            messagebox.showinfo(
                success_title,
                success_msg,
            )
            self.root.destroy()
        except Exception as e:
            err_title = "Upgrade Error" if self.is_upgrade else "Enrollment Error"
            messagebox.showerror(
                err_title, f"Failed to complete operation:\n\n{e}"
            )

    def _deploy_agent_files(self, install_dir: str, config_dir: str) -> None:
        """Copies the running executable and config into the installation directory."""
        deploy_logger = logging.getLogger("agent.installer.deploy")
        deploy_logger.info(f"Creating installation directory: {install_dir}")
        os.makedirs(install_dir, exist_ok=True)

        # Determine source executable path
        if getattr(sys, "frozen", False):
            # Running as PyInstaller bundle: sys.executable is the .exe itself
            source_exe = sys.executable
        else:
            # Running from source: build the exe path from project dist/
            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            source_exe = os.path.join(project_root, "dist", "SentinelAgentSetup.exe")

        target_exe = os.path.join(install_dir, "SentinelAgentService.exe")
        deploy_logger.info(f"Copying {source_exe} -> {target_exe}")

        if not os.path.exists(source_exe):
            raise FileNotFoundError(
                f"Agent executable not found at {source_exe}. "
                f"Build the installer first with scripts/build_installer.py."
            )

        shutil.copy2(source_exe, target_exe)
        deploy_logger.info(f"Deployed service executable: {target_exe}")

        # Also copy config.json into install directory for service discovery
        src_cfg = os.path.join(config_dir, "config.json")
        if os.path.exists(src_cfg):
            dst_cfg = os.path.join(install_dir, "config.json")
            shutil.copy2(src_cfg, dst_cfg)
            deploy_logger.info(f"Deployed config: {dst_cfg}")

        # Create logs subdirectory
        logs_dir = os.path.join(install_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        deploy_logger.info(f"Created logs directory: {logs_dir}")

        # Verify deployment
        if not os.path.exists(target_exe):
            raise RuntimeError(
                f"Deployment verification failed: {target_exe} does not exist after copy."
            )

        size_mb = os.path.getsize(target_exe) / (1024 * 1024)
        deploy_logger.info(
            f"Deployment verification PASSED: {target_exe} ({size_mb:.2f} MB)"
        )

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    wizard = SentinelEnrollmentWizard()
    wizard.run()
