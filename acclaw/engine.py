from enum import Enum, auto
from collections import deque
import logging
from typing import Dict, Any

logger = logging.getLogger("acclaw")

class SystemState(Enum):
    INIT = auto()
    STRUCTURE = auto()
    BOND = auto()
    BUFFER = auto()
    CATALYZE = auto()
    CONTROL = auto()

class ACCEngine:
    """Adaptive Cyclical Control Engine (ACCE)"""

    def __init__(self, max_history: int = 200, stability_target: float = 0.88):
        self.current_state = SystemState.INIT
        self.history: deque = deque(maxlen=max_history)
        self.cycle = 0
        self.consecutive_failures = 0
        self.is_running = False
        self.stability_target = stability_target

        self.thresholds = {
            "stability": 0.80,
            "efficiency": 0.75,
            "temperature_max": 120.0,
            "pressure_max": 300.0
        }
        logger.info("ACCE initialized | Stability target: %.2f", stability_target)

    def collect_feedback(self) -> Dict[str, Any]:
        """Override this in production with real LLM verifier or OpenClaw metrics."""
        try:
            # Simulation mode default (noisy but improving)
            import random
            base = 0.7 + (self.cycle * 0.015)
            data = {
                "stability": min(0.95, base + random.uniform(-0.15, 0.15)),
                "efficiency": min(0.92, base + random.uniform(-0.12, 0.12)),
                "temperature": random.uniform(0.6, 1.1),
                "pressure": random.uniform(180, 280),
            }
            self.history.append(data)
            return data
        except:
            empty = {"stability": 0.0, "efficiency": 0.0, "temperature": 0.0, "pressure": 0.0}
            self.history.append(empty)
            return empty

    def validate(self, feedback: Dict[str, Any]) -> bool:
        if not feedback:
            return False
        return (
            feedback.get("stability", 0.0) >= self.thresholds["stability"] and
            feedback.get("efficiency", 0.0) >= self.thresholds["efficiency"] and
            feedback.get("temperature", 0.0) <= self.thresholds["temperature_max"] and
            feedback.get("pressure", 0.0) <= self.thresholds["pressure_max"]
        )

    def get_average_feedback(self, n: int = 10) -> Dict[str, float]:
        if len(self.history) < n:
            return {"stability": 0.0, "efficiency": 0.0, "temperature": 0.0, "pressure": 0.0}
        recent = list(self.history)[-n:]
        return {
            "stability": sum(d.get("stability", 0.0) for d in recent) / len(recent),
            "efficiency": sum(d.get("efficiency", 0.0) for d in recent) / len(recent),
            "temperature": sum(d.get("temperature", 0.0) for d in recent) / len(recent),
            "pressure": sum(d.get("pressure", 0.0) for d in recent) / len(recent),
        }

    def is_stabilizing(self, n: int = 8) -> bool:
        if len(self.history) < n:
            return False
        recent = [d.get("stability", 0.0) for d in list(self.history)[-n:]]
        return all(s >= self.stability_target for s in recent)

    def next_state(self, feedback: Dict[str, Any]) -> SystemState:
        if not feedback:
            return self._get_next_in_sequence()

        if feedback.get("stability", 0.0) < 0.60:
            logger.info("Low stability → BUFFER")
            return SystemState.BUFFER
        if feedback.get("efficiency", 0.0) < 0.70:
            logger.info("Low efficiency → CATALYZE")
            return SystemState.CATALYZE

        return self._get_next_in_sequence()

    def _get_next_in_sequence(self) -> SystemState:
        sequence = list(SystemState)
        idx = sequence.index(self.current_state)
        return sequence[(idx + 1) % len(sequence)]

    def handle_failure(self, feedback: Dict[str, Any]) -> bool:
        state = self.current_state
        logger.warning(f"Failure in {state.name}")

        if state == SystemState.INIT:
            logger.critical("CRITICAL INIT FAILURE → SHUTDOWN")
            # shutdown_system()  # implement as needed
            return True
        elif state == SystemState.BOND:
            logger.info("BOND failure → Reducing intensity")
            # reduce_reaction_intensity()
        elif state == SystemState.CATALYZE:
            logger.info("CATALYZE failure → Cooling")
            # cool_system()
        else:
            logger.info(f"Non-critical failure in {state.name}")

        self.consecutive_failures += 1
        return False

    def adjust_parameters(self, feedback: Dict[str, Any]):
        if not feedback:
            return
        logger.info(f"Adjusting parameters in {self.current_state.name}")
        # Implement state-specific logic here (e.g. prompt tuning, tool selection)

    def run(self):
        self.is_running = True
        self.cycle = 0
        self.consecutive_failures = 0
        logger.info("=== ACCE Started ===")

        while self.is_running:
            self.cycle += 1
            logger.info(f"[Cycle {self.cycle:04d}] State: {self.current_state.name}")

            try:
                # execute(self.current_state)  # placeholder
                feedback = self.collect_feedback()

                if not self.validate(feedback):
                    if self.handle_failure(feedback):
                        break
                else:
                    self.consecutive_failures = 0

                self.adjust_parameters(feedback)
                self.current_state = self.next_state(feedback)

                if self.is_stabilizing():
                    logger.info("System stabilized → CONTROL mode")
                    self.current_state = SystemState.CONTROL

                if self.consecutive_failures >= 5:
                    logger.warning("Too many failures → Forcing CONTROL")
                    self.current_state = SystemState.CONTROL

            except Exception as e:
                logger.error(f"Error in {self.current_state.name}: {e}")
                if self.handle_failure({"error": str(e)}):
                    break

        logger.info("=== ACCE Stopped ===")

    def get_health(self) -> Dict[str, Any]:
        avg = self.get_average_feedback()
        return {
            "cycle": self.cycle,
            "state": self.current_state.name,
            "avg_stability": round(avg.get("stability", 0), 3),
            "avg_efficiency": round(avg.get("efficiency", 0), 3),
            "consecutive_failures": self.consecutive_failures,
            "is_stable": self.is_stabilizing(),
            "history_size": len(self.history)
        }
