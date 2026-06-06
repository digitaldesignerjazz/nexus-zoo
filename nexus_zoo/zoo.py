"""NexusZoo: the container / simulation world for a population of ZooAgents."""

from __future__ import annotations

import random
from typing import Dict, List, Optional

from .agent import ZooAgent
from .fsm import Event


class NexusZoo:
    """Manages a collection of agents and advances the global simulation."""

    def __init__(self, name: str = "NexusZoo-Alpha") -> None:
        self.name = name
        self.agents: Dict[str, ZooAgent] = {}
        self.tick_count: int = 0
        self.event_log: List[Dict] = []

    def add_agent(self, agent: ZooAgent) -> None:
        if agent.agent_id in self.agents:
            raise ValueError(f"Agent {agent.agent_id} already registered")
        self.agents[agent.agent_id] = agent

    def remove_agent(self, agent_id: str) -> Optional[ZooAgent]:
        return self.agents.pop(agent_id, None)

    def broadcast(self, event: str, intensity: float = 1.0, filter_species: Optional[str] = None) -> int:
        """Send an event to (a subset of) the population. Returns number of agents affected."""
        affected = 0
        for a in self.agents.values():
            if filter_species and a.species != filter_species:
                continue
            if a.receive_event(event, intensity=intensity):
                affected += 1
        self._log("broadcast", {"event": event, "intensity": intensity, "affected": affected})
        return affected

    def tick(self, dt: float = 1.0) -> Dict:
        """Advance the entire zoo by one logical tick."""
        self.tick_count += 1
        snapshots = []
        for agent in list(self.agents.values()):
            snap = agent.step(dt=dt, context={"global_tick": self.tick_count})
            snapshots.append(snap)

        # Global homeostasis / occasional zoo-wide events
        if self.tick_count % 7 == 0 and random.random() < 0.6:
            # A bit of social "weather"
            self.broadcast(Event.STIM_SOCIAL, intensity=0.6)

        if self.tick_count % 11 == 0 and random.random() < 0.35:
            # Subtle threat that makes everyone a little more alert
            self.broadcast(Event.STIM_THREAT, intensity=0.3)

        stats = self._compute_stats(snapshots)
        self._log("tick", {"tick": self.tick_count, "stats": stats})
        return {
            "tick": self.tick_count,
            "population": len(self.agents),
            "stats": stats,
            "snapshots": snapshots,
        }

    def _compute_stats(self, snapshots: List[Dict]) -> Dict:
        if not snapshots:
            return {}
        energies = [s["vector"]["energy"] for s in snapshots]
        curiosities = [s["vector"]["curiosity"] for s in snapshots]
        states = {}
        for s in snapshots:
            st = s["state"]
            states[st] = states.get(st, 0) + 1
        return {
            "avg_energy": sum(energies) / len(energies),
            "avg_curiosity": sum(curiosities) / len(curiosities),
            "state_counts": states,
        }

    def _log(self, kind: str, payload: Dict) -> None:
        self.event_log.append({"t": self.tick_count, "kind": kind, **payload})
        if len(self.event_log) > 500:
            self.event_log = self.event_log[-400:]

    def get_report(self, last_n: int = 5) -> Dict:
        recent = self.event_log[-last_n:] if self.event_log else []
        return {
            "zoo": self.name,
            "ticks": self.tick_count,
            "population": len(self.agents),
            "recent_events": recent,
        }

    def __repr__(self) -> str:
        return f"NexusZoo({self.name}, pop={len(self.agents)}, t={self.tick_count})"
