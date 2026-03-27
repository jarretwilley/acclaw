# acclaw — ACCE for OpenClaw

**Adaptive Cyclical Control Engine for OpenClaw**

Make your OpenClaw agents **safer, more efficient, and self-correcting**.

ACCE adds a structured, adaptive control loop on top of OpenClaw with automatic safety routing, reflection, convergence detection, and anti-oscillation protection.

![ACCE Diagram](docs/acce-diagram.png)

## Features

- 6-phase cycle: `INIT → STRUCTURE → BOND → BUFFER → CATALYZE → CONTROL`
- Safety-first: Low stability (< 0.6) → automatic **BUFFER** (validation/recovery)
- Optimization: Low efficiency (< 0.7) → automatic **CATALYZE** (reflection)
- Convergence detection — stops refining when stable
- Anti-oscillation protection
- Rolling history + system health monitoring
- Easy integration with OpenClaw gateway and tools
- Simulation mode for quick testing

## Installation

```bash
pip install git+https://github.com/jarretwilley/acclaw.git# acclaw
Adaptive Cyclical Control Engine for OpenClaw
