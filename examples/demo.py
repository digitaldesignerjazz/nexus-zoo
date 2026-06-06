#!/usr/bin/env python3
"""NexusZoo demo.

Creates a small population of agents with different NEXUS profiles and personalities,
then runs a simulation so you can observe FSM state changes driven by the evolving
NEXUS State Vectors.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Allow running as script without install
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from nexus_zoo import NexusZoo, ZooAgent  # type: ignore


def load_seed_agents(config_path: Path | None = None) -> list[ZooAgent]:
    if config_path is None:
        config_path = Path(__file__).resolve().parents[1] / "configs" / "default.json"
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    agents: list[ZooAgent] = []
    for a in cfg.get("agents", []):
        agent = ZooAgent.create(
            agent_id=a["id"],
            name=a["name"],
            species=a.get("species", "abstract"),
            vector_seed=a.get("vector"),
            personality=a.get("personality"),
        )
        agents.append(agent)
    return agents


def run_demo(ticks: int = 30, verbose: bool = True) -> NexusZoo:
    zoo = NexusZoo(name="NexusZoo-Demo")
    for agent in load_seed_agents():
        zoo.add_agent(agent)

    if verbose:
        print(f"Starting {zoo.name} with {len(zoo.agents)} agents\n")

    for t in range(1, ticks + 1):
        result = zoo.tick()
        if verbose:
            stats = result["stats"]
            state_str = ", ".join(f"{k}:{v}" for k, v in stats.get("state_counts", {}).items())
            print(
                f"Tick {t:02d} | pop={result['population']} | "
                f"avgE={stats.get('avg_energy', 0):.2f} avgC={stats.get('avg_curiosity', 0):.2f} | "
                f"states=[{state_str}]"
            )
            # Show a couple of agents that recently changed or are interesting
            for snap in result["snapshots"][:2]:
                print(
                    f"  - {snap['name']:<8} ({snap['species']:<8}) state={snap['state']:<6} "
                    f"e={snap['vector']['energy']:+.2f} c={snap['vector']['curiosity']:+.2f}"
                )
        if t == 12:
            # Inject a zoo-wide food event to demonstrate stimulus -> state change
            zoo.broadcast("food", intensity=0.9)
            if verbose:
                print("  >>> Broadcast STIM_FOOD (intensity 0.9) <<<")
    if verbose:
        print("\nFinal report:", zoo.get_report(last_n=3))
    return zoo


def main() -> None:
    ticks = 30
    if len(sys.argv) > 1:
        try:
            ticks = int(sys.argv[1])
        except ValueError:
            pass
    run_demo(ticks=ticks)


if __name__ == "__main__":
    main()
