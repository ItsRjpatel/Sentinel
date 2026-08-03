import subprocess
import logging
import time
import tempfile
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)

def handle_custom_script(command: Dict[str, Any]) -> Dict[str, Any]:
    """Handles execution of CUSTOM_SCRIPT commands (PowerShell, CMD, Batch)."""
    payload = command.get("payload", {}) or {}
    shell = (payload.get("shell") or "powershell").lower()
    script_text = payload.get("script", "")
    timeout = payload.get("timeout", 300)
    capture_output = payload.get("capture_output", True)
    
    if not script_text.strip():
        return {
            "success": False,
            "error": "No script content provided in command payload",
            "exit_code": -1
        }

    start_time = time.time()
    
    try:
        if shell == "powershell":
            cmd_args = [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy", "Bypass",
                "-Command", script_text
            ]
        elif shell in ["cmd", "batch"]:
            # Write script to temporary batch file if multi-line
            if "\n" in script_text:
                with tempfile.NamedTemporaryFile("w", suffix=".bat", delete=False) as tf:
                    tf.write(script_text)
                    tf_path = tf.name
                cmd_args = ["cmd.exe", "/c", tf_path]
            else:
                cmd_args = ["cmd.exe", "/c", script_text]
        else:
            return {
                "success": False,
                "error": f"Unsupported shell type: {shell}",
                "exit_code": -1
            }

        res = subprocess.run(
            cmd_args,
            timeout=timeout,
            capture_output=capture_output,
            text=True,
            check=False
        )

        duration_ms = int((time.time() - start_time) * 1000)

        # Cleanup temp file if created
        if shell in ["cmd", "batch"] and "\n" in script_text and 'tf_path' in locals():
            try:
                os.remove(tf_path)
            except Exception:
                pass

        return {
            "success": res.returncode == 0,
            "stdout": (res.stdout or "").strip(),
            "stderr": (res.stderr or "").strip(),
            "exit_code": res.returncode,
            "shell": shell,
            "duration_ms": duration_ms
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout} seconds",
            "exit_code": -1
        }
    except Exception as e:
        logger.error(f"Failed to execute custom script ({shell}): {e}")
        return {
            "success": False,
            "error": str(e),
            "exit_code": -1
        }
