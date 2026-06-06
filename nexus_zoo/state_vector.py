"""NEXUS State Vector implementation.

A structured, semantically-labeled multi-dimensional state for agents.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple


DEFAULT_DIMENSIONS: List[str] = [
    "energy",      # physical / metabolic resource
    "curiosity",   # drive to explore / try new things
    "cohesion",    # social / group bonding tendency
    "stability",   # resistance to rapid state change
    "entropy",     # disorder / unpredictability (high = chaotic)
    "valence",     # overall affective tone (positive <-> negative)
]


@dataclass
class NEXUSStateVector:
    """NEXUS (Neural EXperiential Unified State) vector.

    Values are kept in roughly [-1.0, 2.0] range but not strictly clamped
    except during explicit normalization.
    """

    values: Dict[str, float] = field(default_factory=dict)
    dimensions: List[str] = field(default_factory=lambda: DEFAULT_DIMENSIONS.copy())

    def __post_init__(self) -> None:
        if not self.values:
            # Sensible neutral-ish default
            self.values = {d: 0.5 for d in self.dimensions}
        else:
            # Ensure all declared dimensions exist
            for d in self.dimensions:
                self.values.setdefault(d, 0.0)

    @classmethod
    def from_dict(cls, data: Dict[str, float], dimensions: Iterable[str] | None = None) -> "NEXUSStateVector":
        dims = list(dimensions) if dimensions else list(data.keys())
        vec = cls(dimensions=dims)
        vec.values.update({k: float(v) for k, v in data.items() if k in dims})
        return vec

    def clone(self) -> "NEXUSStateVector":
        return NEXUSStateVector(
            values=self.values.copy(),
            dimensions=self.dimensions.copy(),
        )

    def get(self, dim: str) -> float:
        return self.values.get(dim, 0.0)

    def set(self, dim: str, value: float) -> None:
        if dim not in self.values:
            self.dimensions.append(dim)
        self.values[dim] = float(value)

    def to_array(self) -> List[float]:
        return [self.values.get(d, 0.0) for d in self.dimensions]

    def magnitude(self) -> float:
        return math.sqrt(sum(v * v for v in self.values.values()))

    def normalize(self, target: float = 1.0) -> None:
        mag = self.magnitude()
        if mag < 1e-9:
            return
        scale = target / mag
        for d in self.values:
            self.values[d] *= scale

    def blend(self, other: "NEXUSStateVector", weight: float = 0.5) -> "NEXUSStateVector":
        """Return a new vector that is a coherent 'nexus' blend of self and other."""
        w = max(0.0, min(1.0, weight))
        result = self.clone()
        for d in result.dimensions:
            ov = other.get(d)
            result.values[d] = (1.0 - w) * result.values[d] + w * ov
        return result

    def mutate(self, intensity: float = 0.08, dims: Iterable[str] | None = None) -> None:
        """In-place small random mutation (models internal drift / experience)."""
        target_dims = list(dims) if dims else self.dimensions
        for d in target_dims:
            if d in self.values:
                jitter = random.gauss(0.0, intensity)
                self.values[d] += jitter

    def distance(self, other: "NEXUSStateVector") -> float:
        """Euclidean distance across shared dimensions."""
        total = 0.0
        for d in set(self.dimensions) & set(other.dimensions):
            diff = self.values[d] - other.values.get(d, 0.0)
            total += diff * diff
        return math.sqrt(total)

    def as_dict(self) -> Dict[str, float]:
        return {d: self.values.get(d, 0.0) for d in self.dimensions}

    def __repr__(self) -> str:
        short = ", ".join(f"{d}={self.values[d]:+.2f}" for d in self.dimensions[:4])
        return f"NEXUSStateVector({short}...)"
