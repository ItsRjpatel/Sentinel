import pytest
import os
import sys
from pathlib import Path

# Add project root directory to sys.path so 'agent' can be imported in tests
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
