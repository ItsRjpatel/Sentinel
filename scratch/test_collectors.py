import asyncio
import sys
import os

from agent.collectors.software.collector import SoftwareCollector
from agent.collectors.services.collector import WindowsServiceCollector
from agent.collectors.network.collector import NetworkCollector
from agent.collectors.windows_updates.collector import WindowsUpdateCollector

def run_tests():
    import pythoncom
    pythoncom.CoInitialize()
    try:
        print("--- Software ---")
        sc = SoftwareCollector()
        softs = sc.collect()
        print(f"Software count: {len(softs)}")
        if len(softs) > 0:
            print(softs[0].model_dump())

        print("\n--- Services ---")
        svc = WindowsServiceCollector()
        svcs = svc.collect()
        print(f"Services count: {len(svcs)}")
        if len(svcs) > 0:
            print(svcs[0].model_dump())

        print("\n--- Network ---")
        nc = NetworkCollector()
        nets = nc.collect()
        print(f"Network count: {len(nets)}")
        if len(nets) > 0:
            print(nets[0].model_dump())

        print("\n--- Windows Updates ---")
        wc = WindowsUpdateCollector()
        wus = wc.collect()
        print(f"Windows Updates count: {len(wus)}")
        if len(wus) > 0:
            print(wus[0].model_dump())

    except Exception as e:
        print(f"Error: {e}")
    finally:
        pythoncom.CoUninitialize()

if __name__ == "__main__":
    run_tests()
