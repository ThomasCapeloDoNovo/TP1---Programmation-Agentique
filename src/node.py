from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass(slots=True)
class Node:
    state: Any
    parent: Optional["Node"]
    action: Any
    g: float      # coût du chemin depuis l'état initial
    depth: int

    def path(self) -> List["Node"]:
        node, out = self, []
        while node:
            out.append(node)
            node = node.parent
        return out[::-1]
