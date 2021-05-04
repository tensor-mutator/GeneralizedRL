"""
@author: Debajyoti Raychaudhuri

Implements game tree to run Monte-Carlo Search on
"""

from multiprocessing import Lock, Array
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Iterator, Dict
from .exceptions import TreeError
from ...colors import COLORS

__all__ = ["Tree"]

@dataclass
class Node:
      """
          Represents a node of the tree
      """

      edges: Dict = field(default_factory=lambda: defaultdict(lambda: Edge))
      sum_n: int = 0

@dataclass
class Edge:
      """
          Represents an edge of the tree
      """

      n: int = 0
      w: float = 0
      q: float = 0
      p: float = 0

class Tree:
      """
          Implements a game tree
      """

      def __init__(self, depth: int, branching_factor: int, virtual_loss: float) -> None:
          self._lock = defaultdict(lambda: Lock)
          self._depth = depth
          self._branching_factor = branching_factor
          self._virtual_loss = virtual_loss
          self._tree = defaultdict(lambda: Node)

      def __iter__(self) -> Iterator:
          return list(self._tree.keys())

      def __getitem__(self, state: str) -> List[Edge]:
          return self._tree[state].edges

      def __contains__(self, state: str) -> bool:
          return state in self._tree.keys()

      def expand(self, state: str, policy: List[float], actions: List[str]) -> None:
          """
              Expands the tree with a node
          """

          if len(policy) > self._branching_factor:
             raise TreeError("Number of edges attached to the node exceeds the branching factor of the tree: {}{} > {}{}".format(COLOR.RED,
                                                                                                                                 len(policy),
                                                                                                                                 COLOR.MAGENTA,
                                                                                                                                 self._branching_factor))
          normalizing_factor = sum(policy)+1e-08
          for action, p in zip(actions, policy):
              self._tree[state].edges[action].p = p/normalizing_factor

      def simulate(self, state: str, action: str) -> None:
          """
              Traverses a node while applying virtual loss
          """

          with self._lock(state):
               node = self._tree[state]
               node.sum_n += self._virtual_loss
               edge = node.edges[action]
               edge.n += self._virtual_loss
               edge.w += -self._virtual_loss
               edge.q = edge.w/edge.n

      def backpropagate(self, state: str, value: float) -> None:
          """
              Updates the visitation frequency and the action value of a node
          """

          with self._lock(state):
               node = self._tree[state]
               node.sum_n += -self._virtual_loss + 1
               edge = node.edges[action]
               edge.n += -self._virtual_loss + 1
               edge.w += self._virtual_loss + value
               edge.q = edge.w/edge.n
