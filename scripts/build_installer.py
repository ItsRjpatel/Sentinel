import os
import sys
import subprocess
import shutil
import time
from pathlib import Path

def build_executable():
    """Compiles Sentinel Agent executable using PyInstaller with cache purging."""
    root_dir = Path(__file__).parent.parent.resolve()
    spec_path = root_dir / "sentinel_agent.spec"
    dist_dir = root_dir / "dist"
    build_dir = root_dir / "build"
    setup_exe = dist_dir / "SentinelAgentSetup.exe"

    print("==================================================")
    print("Building Endpoint Sentinel X Windows Agent Binary ")
    print("==================================================")
    print(f"Root Directory: {root_dir}")
    print(f"Spec File: {spec_path}")

    # Terminate any running SentinelAgentSetup processes
    if os.name == "nt":
        try:
            subprocess.run("taskkill /f /im SentinelAgentSetup.exe", shell=True, capture_output=True)
            time.sleep(1)
        except Exception:
            pass

    # Purge stale dist and build directories with retry loop
    for attempt in range(3):
        try:
            if setup_exe.exists():
                setup_exe.unlink()
            if build_dir.exists():
                shutil.rmtree(build_dir, ignore_errors=True)
            break
        except Exception as e:
            print(f"Attempt {attempt+1}: waiting for file lock release ({e})...")
            time.sleep(1)

    pyinstaller_bin = shutil.which("pyinstaller")
    if not pyinstaller_bin:
        pyinstaller_cmd = [sys.executable, "-m", "PyInstaller", str(spec_path), "--noconfirm", "--clean"]
    else:
        pyinstaller_cmd = [pyinstaller_bin, str(spec_path), "--noconfirm", "--clean"]

    try:
        print("Executing PyInstaller compilation with --clean...")
        res = subprocess.run(pyinstaller_cmd, cwd=str(root_dir), check=True)
        print("PyInstaller build completed successfully.")

        if setup_exe.exists():
            size_mb = setup_exe.stat().st_size / (1024 * 1024)
            print(f"SUCCEEDED: Artifact generated at {setup_exe} ({size_mb:.2f} MB)")
            return True
        else:
            print(f"WARNING: PyInstaller finished but {setup_exe} was not found.")
            return False
    except Exception as e:
        print(f"ERROR: Build failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = build_executable()
    sys.exit(0 if success else 1)
