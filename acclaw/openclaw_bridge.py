import requests
from .engine import ACCEngine, SystemState
from typing import Dict, Any

class OpenClawBridge:
    def __init__(self, engine: ACCEngine, gateway_url: str = "http://localhost:8000"):
        self.engine = engine
        self.gateway_url = gateway_url

    def inject_session(self, openclaw_data: Dict[str, Any]):
        feedback = {
            "stability": openclaw_data.get("confidence", 0.8),
            "efficiency": openclaw_data.get("success_rate", 0.75),
            "source": "openclaw",
            **openclaw_data
        }
        self.engine.history.append(feedback)

    def export_result(self) -> Dict[str, Any]:
        return {
            "accc_health": self.engine.get_health(),
            "final_output": "Task completed via ACCE-controlled workflow",
        }
