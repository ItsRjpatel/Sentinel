import os
import logging
from typing import List, Dict, Any
from agent.collectors.software.models import SoftwareInventoryData
from agent.collectors.software.mapper import map_raw_registry_entry
from agent.collectors.software.validator import filter_software_list

logger = logging.getLogger(__name__)

IS_WINDOWS = os.name == "nt"

class SoftwareCollector:
    """Discovers installed software applications directly from HKLM and HKCU Windows Registry hives."""

    REGISTRY_TARGETS = [
        # (Hive, Subkey Path, Architecture, InstallScope)
        ("HKLM", r"Software\Microsoft\Windows\CurrentVersion\Uninstall", "x64", "Per-machine"),
        ("HKLM", r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall", "x86", "Per-machine"),
        ("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Uninstall", "x64", "Per-user"),
    ]

    def collect(self) -> List[SoftwareInventoryData]:
        """Queries registry hives and returns validated software DTO list."""
        if not IS_WINDOWS:
            logger.info("Collector executing on non-Windows platform. Returning stub software inventory.")
            stub_entries = [
                {
                    "DisplayName": "Google Chrome",
                    "Publisher": "Google LLC",
                    "DisplayVersion": "120.0.6099.109",
                    "InstallDate": "20260115",
                    "InstallLocation": "/usr/bin/google-chrome",
                    "EstimatedSize": 450000,
                    "UninstallString": "/usr/bin/google-chrome --uninstall",
                    "InstallSource": "",
                    "Architecture": "x64",
                    "Language": "1033",
                    "ProductCode": "{STUB-CHROME-GUID}",
                    "SystemComponent": 0,
                    "WindowsInstaller": 0,
                    "URLInfoAbout": "https://www.google.com/chrome",
                    "HelpLink": "",
                    "ModifyPath": "",
                    "InstallScope": "Per-machine",
                    "RegistryKey": "STUB/SOFTWARE/Google/Chrome"
                },
                {
                    "DisplayName": "Visual Studio Code",
                    "Publisher": "Microsoft Corporation",
                    "DisplayVersion": "1.85.1",
                    "InstallDate": "20260201",
                    "InstallLocation": "/usr/share/code",
                    "EstimatedSize": 350000,
                    "UninstallString": "/usr/share/code/uninstall",
                    "InstallSource": "",
                    "Architecture": "x64",
                    "Language": "1033",
                    "ProductCode": "{STUB-VSCODE-GUID}",
                    "SystemComponent": 0,
                    "WindowsInstaller": 0,
                    "URLInfoAbout": "https://code.visualstudio.com",
                    "HelpLink": "",
                    "ModifyPath": "",
                    "InstallScope": "Per-machine",
                    "RegistryKey": "STUB/SOFTWARE/Microsoft/VSCode"
                }
            ]
            return filter_software_list(stub_entries, map_raw_registry_entry)

        import winreg

        raw_entries: List[Dict[str, Any]] = []

        hive_map = {
            "HKLM": winreg.HKEY_LOCAL_MACHINE,
            "HKCU": winreg.HKEY_CURRENT_USER
        }

        for hive_name, subkey_path, default_arch, scope in self.REGISTRY_TARGETS:
            hive = hive_map.get(hive_name)
            if not hive:
                continue

            try:
                # Access registry key with READ permissions
                key = winreg.OpenKey(hive, subkey_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
            except OSError as e:
                logger.debug(f"Could not open registry path {hive_name}\\{subkey_path}: {e}")
                continue

            try:
                subkey_count, _, _ = winreg.QueryInfoKey(key)
                for i in range(subkey_count):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        full_subkey_path = f"{subkey_path}\\{subkey_name}"
                        sub_handle = winreg.OpenKey(key, subkey_name, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
                        
                        raw_dict = {
                            "RegistryKey": f"{hive_name}\\{full_subkey_path}",
                            "InstallScope": scope,
                            "Architecture": default_arch,
                            "ProductCode": subkey_name if subkey_name.startswith("{") and subkey_name.endswith("}") else ""
                        }

                        # Enumerate all values under the uninstall key
                        _, val_count, _ = winreg.QueryInfoKey(sub_handle)
                        for j in range(val_count):
                            val_name, val_data, _ = winreg.EnumValue(sub_handle, j)
                            raw_dict[val_name] = val_data

                        winreg.CloseKey(sub_handle)

                        # Only add if DisplayName exists
                        if raw_dict.get("DisplayName"):
                            raw_entries.append(raw_dict)
                    except OSError:
                        continue
            except OSError as e:
                logger.warning(f"Error enumerating keys under {hive_name}\\{subkey_path}: {e}")
            finally:
                winreg.CloseKey(key)

        return filter_software_list(raw_entries, map_raw_registry_entry)
