import os
import sys
import shutil
import argparse
import subprocess
import logging

logger = logging.getLogger("agent.uninstaller")

def run_uninstaller(purge: bool = False):
    """Performs clean uninstallation of Sentinel Agent service, files, and registry entries."""
    logger.info("Starting Endpoint Sentinel Agent Uninstallation...")

    if os.name == "nt":
        # 1. Stop and Delete Windows Service
        logger.info("Stopping and removing SentinelAgent service...")
        try:
            subprocess.run("net stop SentinelAgent", shell=True, capture_output=True)
            subprocess.run("sc.exe delete SentinelAgent", shell=True, capture_output=True)
            logger.info("SentinelAgent service deleted.")
        except Exception as e:
            logger.warning(f"Error removing Windows service: {e}")

        # 2. Remove Installation Directory
        inst_dir = os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "Endpoint Sentinel")
        if os.path.exists(inst_dir):
            try:
                shutil.rmtree(inst_dir, ignore_errors=True)
                logger.info(f"Removed installation directory: {inst_dir}")
            except Exception as e:
                logger.error(f"Failed to remove installation directory: {e}")

        # 3. Optional ProgramData Cleanup
        if purge:
            prog_data = os.environ.get("PROGRAMDATA", "C:\\ProgramData")
            data_dir = os.path.join(prog_data, "EndpointSentinel")
            if os.path.exists(data_dir):
                try:
                    shutil.rmtree(data_dir, ignore_errors=True)
                    logger.info(f"Removed data directory: {data_dir}")
                except Exception as e:
                    logger.error(f"Failed to remove data directory: {e}")
        else:
            logger.info("Preserving configuration data per standard uninstall behavior.")

        # 4. Remove Registry Uninstall Key
        try:
            reg_cmd = 'reg delete "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\EndpointSentinel" /f'
            subprocess.run(reg_cmd, shell=True, capture_output=True)
            logger.info("Registry uninstall entry removed.")
        except Exception as e:
            logger.warning(f"Error deleting registry key: {e}")

    logger.info("Endpoint Sentinel Agent uninstallation completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Endpoint Sentinel Agent Uninstaller")
    parser.add_argument("--purge", action="store_true", help="Force wipe of agent configuration and identity data")
    args = parser.parse_args()

    run_uninstaller(purge=args.purge)
