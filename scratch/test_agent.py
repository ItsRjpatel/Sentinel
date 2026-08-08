import os
import asyncio
import sys
import logging

# Override PROGRAMDATA
os.environ["PROGRAMDATA"] = r"d:\App_New_\Sentinel\local_data"
os.makedirs(r"d:\App_New_\Sentinel\local_data\EndpointSentinel", exist_ok=True)

# Write a dummy config.json so it knows the server URL
import json
config_path = r"d:\App_New_\Sentinel\local_data\EndpointSentinel\config.json"
if not os.path.exists(config_path):
    with open(config_path, "w") as f:
        json.dump({
            "server_url": "http://127.0.0.1:8001/api/v1",
            "enrollment_secret": "sentinel-secret-key-change-in-production"
        }, f)
else:
    with open(config_path, "r") as f:
        data = json.load(f)
    data["server_url"] = "http://127.0.0.1:8001/api/v1"
    with open(config_path, "w") as f:
        json.dump(data, f)

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Now run the agent
sys.argv = ["agent", "run"]
from agent.main import main
asyncio.run(main())
