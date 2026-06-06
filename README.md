# NexusZoo

NexusZoo is a minimal Python prototype exploring **NEXUS State Vectors** and **FSM-driven agents** living together in a simulated "zoo".

## Core Concepts

- **NEXUS State Vector**: A structured, multi-dimensional continuous state (energy, curiosity, cohesion, entropy, valence, etc.). Supports blending, mutation, distance metrics, and "nexus" operations (coherent mixing between agents).
- **FSM Agents**: Each agent is driven by a lightweight Finite State Machine. States include IDLE, ROAM, FEED, SOCIAL, REST, ALERT. Transitions are triggered by internal thresholds (from the state vector) or external events.
- **The Zoo**: A manager that hosts a population of agents, advances global time, broadcasts stimuli, and collects statistics.

This is an initial exploratory prototype (no external dependencies beyond Python 3.10+).

## Quick Start

```bash
python -m examples.demo
# or
python examples/demo.py
```

## Project Layout

```
nexus-zoo/
├── nexus_zoo/
│   ├── __init__.py
│   ├── state_vector.py   # NEXUSStateVector
│   ├── fsm.py            # FiniteStateMachine + States
│   ├── agent.py          # ZooAgent (StateVector + FSM)
│   └── zoo.py            # NexusZoo simulation container
├── examples/
│   └── demo.py
├── configs/
│   └── default.json
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Running the Demo

The demo instantiates a small population with varied "personalities" (different starting vectors and transition biases), then runs a number of ticks. Watch agents transition between behavioral states as their internal NEXUS vectors evolve.

## Future Directions (ideas)

- Persistent state snapshots
- Richer event system and inter-agent messaging
- Visualization (matplotlib / textual)
- Pluggable transition policies / learned policies
- Export of state trajectories for analysis
- Integration with larger Nexus ecosystem (orchestrator, mesh)

## License

Prototype / research use. See LICENSE if present.
