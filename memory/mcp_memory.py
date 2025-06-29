# memory/mcp_memory.py

import json
from pathlib import Path
from typing import Any, Dict, List

class MCPMemory:
    """
    JSON-backed Model Context Protocol memory.
    Stores a list of session dicts at `context_store/mcp.json`.
    Each record includes: id, timestamp, messages, tool_calls, outcome, self_reflection.
    """
    def __init__(self, file_path: str = "context_store/mcp.json"):
        self.path = Path(file_path)
        self._bootstrap()

    def _bootstrap(self) -> None:
        # Ensure directory exists and JSON file is initialized
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({"sessions": []}, indent=2))

    def load(self) -> List[Dict[str, Any]]:
        """Return the list of session records."""
        data = json.loads(self.path.read_text())
        return data.get("sessions", [])

    def append(self, record: Dict[str, Any]) -> None:
        """Append a new session record and save."""
        data = json.loads(self.path.read_text())
        data.setdefault("sessions", []).append(record)
        self.path.write_text(json.dumps(data, indent=2))
