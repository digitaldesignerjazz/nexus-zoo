"""NexusZoo: NEXUS State Vector + FSM agents prototype."""

from .state_vector import NEXUSStateVector
from .fsm import State, FiniteStateMachine
from .agent import ZooAgent
from .zoo import NexusZoo

__all__ = [
    "NEXUSStateVector",
    "State",
    "FiniteStateMachine",
    "ZooAgent",
    "NexusZoo",
]

__version__ = "0.1.0"
