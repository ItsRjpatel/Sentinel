import os
import sys
import time
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from pathlib import Path
from agent.utils.config import load_settings
from agent.utils.diagnostics import collect_diagnostics_archive

def open_logs_folder():
    """Opens the logs directory in Windows File Explorer."""
    prog_data = os.environ.get("PROGRAMDATA", "C:\\ProgramData")
    logs_dir = os.path.join(prog_data, "EndpointSentinel", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    if os.name == "nt":
        os.startfile(logs_dir)

def restart_agent_service():
    """Restarts the SentinelAgent Windows Service via net stop / start."""
    try:
        if os.name == "nt":
            subprocess.run("net stop SentinelAgent && net start SentinelAgent", shell=True, check=True)
            messagebox.showinfo("Sentinel Agent", "SentinelAgent service restarted successfully.")
        else:
            messagebox.showinfo("Sentinel Agent", "Service restart triggered.")
    except Exception as e:
        messagebox.showerror("Sentinel Agent Error", f"Failed to restart service: {e}")

def run_inventory_scan():
    """Triggers an immediate background inventory scan cycle."""
    try:
        config = load_settings()
        # Launch background python subprocess to trigger agent scan
        agent_exec = sys.executable
        subprocess.Popen([agent_exec, "-m", "agent.main", "run"], shell=False)
        messagebox.showinfo("Sentinel Agent", "Inventory scan cycle dispatched successfully.")
    except Exception as e:
        messagebox.showerror("Sentinel Agent Error", f"Failed to trigger inventory scan: {e}")

def run_diagnostics_collection():
    """Collects system diagnostics ZIP archive."""
    try:
        zip_path = collect_diagnostics_archive()
        messagebox.showinfo("Sentinel Diagnostics", f"Diagnostics archive created successfully at:\n\n{zip_path}")
        # Open directory containing the zip
        os.startfile(os.path.dirname(zip_path))
    except Exception as e:
        messagebox.showerror("Diagnostics Error", f"Failed to collect diagnostics: {e}")

def show_about_dialog():
    """Displays About Sentinel Agent dialog."""
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(
        "About Endpoint Sentinel X Agent",
        "Endpoint Sentinel X Agent v0.9.0\n"
        "Enterprise Windows Endpoint Security & Management Daemon\n\n"
        "Copyright © 2026 Sentinel Security Inc. All rights reserved."
    )
    root.destroy()

class AgentTrayApp:
    def __init__(self):
        self.config = load_settings()
        self.is_running = True
        self.last_sync = datetime.now().strftime("%H:%M:%S")

    def run(self):
        """Runs the system tray icon application loop using pystray or Tkinter fallback."""
        try:
            import pystray
            from PIL import Image, ImageDraw

            # Generate tray icon image (Green circle dot indicator)
            image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            draw.ellipse((8, 8, 56, 56), fill=(16, 185, 129))  # Emerald 500
            draw.ellipse((20, 20, 44, 44), fill=(255, 255, 255))

            def on_exit(icon, item):
                icon.stop()

            menu = pystray.Menu(
                pystray.MenuItem(f"Connected: {self.config.server_url}", lambda: None, enabled=False),
                pystray.MenuItem(f"Last Sync: {self.last_sync}", lambda: None, enabled=False),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Run Inventory Now", lambda: run_inventory_scan()),
                pystray.MenuItem("Restart Agent Service", lambda: restart_agent_service()),
                pystray.MenuItem("Open Logs Folder", lambda: open_logs_folder()),
                pystray.MenuItem("Collect Diagnostics", lambda: run_diagnostics_collection()),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("About Endpoint Sentinel", lambda: show_about_dialog()),
                pystray.MenuItem("Exit Tray", on_exit)
            )

            icon = pystray.Icon("SentinelAgent", image, "Endpoint Sentinel X Agent", menu)
            icon.run()
        except ImportError:
            # Fallback Tkinter dialog if pystray/PIL is not installed in local environment
            show_about_dialog()

if __name__ == "__main__":
    app = AgentTrayApp()
    app.run()
