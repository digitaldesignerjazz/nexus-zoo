"""Finite State Machine for NexusZoo agents."""

from __future__ import annotations

from enum import Enum, auto
from typing import Callable, Dict, List, Optional, Tuple


class State(Enum):
    IDLE = auto()
    ROAM = auto()
    FEED = auto()
    SOCIAL = auto()
    REST = auto()
    ALERT = auto()


# Event vocabulary (simple strings for the prototype)
class Event:
    TICK = "tick"
    STIM_FOOD = "food"
    STIM_SOCIAL = "social"
    STIM_THREAT = "threat"
    ENERGY_LOW = "energy_low"
    ENERGY_HIGH = "energy_high"
    CURIOSITY_HIGH = "curiosity_high"
    COHESION_HIGH = "cohesion_high"


Transition = Tuple[State, str]  # (from_state, event) -> to_state


class FiniteStateMachine:
    """Lightweight FSM with threshold-driven and event-driven transitions.

    The prototype keeps transition rules declarative and overridable per agent.
    """

    def __init__(self, initial: State = State.IDLE) -> None:
        self.current: State = initial
        self.history: List[State] = [initial]
        # Default transition table: (from_state, event) -> to_state
        self._transitions: Dict[Transition, State] = self._default_transitions()

    def _default_transitions(self) -> Dict[Transition, State]:
        t: Dict[Transition, State] = {}
        # Core survival / exploration loop
        t[(State.IDLE, Event.TICK)] = State.ROAM
        t[(State.ROAM, Event.TICK)] = State.IDLE
        t[(State.ROAM, Event.STIM_FOOD)] = State.FEED
        t[(State.FEED, Event.TICK)] = State.IDLE
        t[(State.IDLE, Event.ENERGY_LOW)] = State.FEED
        t[(State.FEED, Event.ENERGY_HIGH)] = State.ROAM

        # Social drive
        t[(State.IDLE, Event.COHESION_HIGH)] = State.SOCIAL
        t[(State.ROAM, Event.COHESION_HIGH)] = State.SOCIAL
        t[(State.SOCIAL, Event.TICK)] = State.IDLE
        t[(State.SOCIAL, Event.STIM_SOCIAL)] = State.SOCIAL

        # Rest & recovery
        t[(State.IDLE, Event.ENERGY_LOW)] = State.REST
        t[(State.REST, Event.TICK)] = State.IDLE
        t[(State.REST, Event.ENERGY_HIGH)] = State.ROAM

        # Threat / alert
        t[(State.ROAM, Event.STIM_THREAT)] = State.ALERT
        t[(State.IDLE, Event.STIM_THREAT)] = State.ALERT
        t[(State.ALERT, Event.TICK)] = State.ROAM
        t[(State.SOCIAL, Event.STIM_THREAT)] = State.ALERT

        # Curiosity spike
        t[(State.IDLE, Event.CURIOSITY_HIGH)] = State.ROAM
        t[(State.REST, Event.CURIOSITY_HIGH)] = State.ROAM
        return t

    def add_transition(self, from_state: State, event: str, to_state: State) -> None:
        self._transitions[(from_state, event)] = to_state

    def can_transition(self, event: str) -> bool:
        return (self.current, event) in self._transitions

    def process(self, event: str, context: Optional[Dict] = None) -> bool:
        """Attempt a transition on the given event. Returns True if state changed."""
        key = (self.current, event)
        if key in self._transitions:
            next_state = self._transitions[key]
            if next_state != self.current:
                self.current = next_state
                self.history.append(self.current)
                return True
        # Fallback: some events can be interpreted as generic TICK for exploration
        if event != Event.TICK and (self.current, Event.TICK) in self._transitions:
            # Only do implicit tick if no direct handler existed
            pass
        return False

    def force(self, new_state: State) -> None:
        if new_state != self.current:
            self.current = new_state
            self.history.append(self.current)

    def __repr__(self) -> str:
        return f"FSM({self.current.name}, history_len={len(self.history)})"
