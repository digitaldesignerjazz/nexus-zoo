"""ZooAgent: an agent powered by a NEXUS State Vector and an FSM."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, Optional

from .fsm import Event, FiniteStateMachine, State
from .state_vector import NEXUSStateVector


@dataclass
class ZooAgent:
    """A single inhabitant of the NexusZoo.

    The agent's behavior emerges from the interplay of:
    - its NEXUS state vector (continuous internal state)
    - its FSM (discrete behavioral mode)
    - a small personality vector (biases)
    """

    agent_id: str
    name: str
    species: str = "abstract"
    vector: NEXUSStateVector = field(default_factory=NEXUSStateVector)
    fsm: FiniteStateMachine = field(default_factory=FiniteStateMachine)
    personality: Dict[str, float] = field(default_factory=lambda: {
        "exploration_bias": 0.5,
        "social_bias": 0.5,
        "rest_bias": 0.3,
    })

    step_count: int = 0
    last_event: Optional[str] = None

    @classmethod
    def create(
        cls,
        agent_id: str,
        name: str,
        species: str,
        vector_seed: Optional[Dict[str, float]] = None,
        personality: Optional[Dict[str, float]] = None,
    ) -> "ZooAgent":
        vec = NEXUSStateVector.from_dict(vector_seed) if vector_seed else NEXUSStateVector()
        pers = personality or {}
        return cls(
            agent_id=agent_id,
            name=name,
            species=species,
            vector=vec,
            personality={**cls.__dataclass_fields__["personality"].default_factory(), **pers},
        )

    def receive_event(self, event: str, intensity: float = 1.0) -> bool:
        """Inject an external or internal stimulus. May cause state transition + vector change."""
        self.last_event = event
        changed = self.fsm.process(event)

        # Modulate vector based on event type (very lightweight "physiology")
        if event == Event.STIM_FOOD:
            self.vector.values["energy"] = min(1.8, self.vector.get("energy") + 0.35 * intensity)
            self.vector.values["valence"] += 0.1
        elif event == Event.STIM_SOCIAL:
            self.vector.values["cohesion"] = min(1.6, self.vector.get("cohesion") + 0.25 * intensity)
            self.vector.values["valence"] += 0.08
        elif event == Event.STIM_THREAT:
            self.vector.values["entropy"] = min(1.8, self.vector.get("entropy") + 0.4 * intensity)
            self.vector.values["stability"] = max(-0.5, self.vector.get("stability") - 0.3)
            self.vector.values["valence"] -= 0.25
            self.fsm.force(State.ALERT)
            changed = True
        elif event == Event.ENERGY_LOW:
            self.vector.values["energy"] = max(0.0, self.vector.get("energy") - 0.1)
        elif event == Event.CURIOSITY_HIGH:
            self.vector.values["curiosity"] = min(1.7, self.vector.get("curiosity") + 0.2)

        # Small mutation from experience
        self.vector.mutate(intensity=0.015)
        return changed

    def step(self, dt: float = 1.0, context: Optional[Dict] = None) -> Dict:
        """Advance the agent one logical time step. Returns a small status snapshot."""
        self.step_count += 1
        ctx = context or {}

        # 1. Natural drift / homeostatic tendencies
        self.vector.values["energy"] = max(0.05, self.vector.get("energy") - 0.02 * dt)
        self.vector.values["entropy"] = max(0.0, self.vector.get("entropy") - 0.01 * dt)  # slow calming
        self.vector.mutate(intensity=0.012 * dt)

        # 2. Derive internal events from vector thresholds (the "NEXUS" part)
        internal_events: list[str] = []
        if self.vector.get("energy") < 0.35:
            internal_events.append(Event.ENERGY_LOW)
        if self.vector.get("energy") > 1.35:
            internal_events.append(Event.ENERGY_HIGH)
        if self.vector.get("curiosity") > 1.1 + self.personality.get("exploration_bias", 0.5) * 0.3:
            internal_events.append(Event.CURIOSITY_HIGH)
        if self.vector.get("cohesion") > 1.15 + self.personality.get("social_bias", 0.5) * 0.4:
            internal_events.append(Event.COHESION_HIGH)

        state_changed = False
        for ev in internal_events:
            if self.receive_event(ev):
                state_changed = True

        # 3. Default TICK behavior (exploration / idle oscillation)
        if not state_changed:
            self.receive_event(Event.TICK)

        # 4. Occasional random micro-behaviors (makes the zoo feel alive)
        if random.random() < 0.08 * self.personality.get("exploration_bias", 0.5):
            if self.fsm.current in (State.IDLE, State.ROAM):
                self.vector.values["curiosity"] = min(1.6, self.vector.get("curiosity") + 0.1)

        return self.get_status()

    def get_status(self) -> Dict:
        return {
            "id": self.agent_id,
            "name": self.name,
            "species": self.species,
            "state": self.fsm.current.name,
            "steps": self.step_count,
            "vector": self.vector.as_dict(),
            "last_event": self.last_event,
        }

    def __repr__(self) -> str:
        return f"ZooAgent({self.name}, {self.species}, {self.fsm.current.name})"
