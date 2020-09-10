from abc import ABCMeta, abstractmethod
from typing import Any, Sequence, Dict, Tuple
import numpy as np

__all__ = ["Environment"]

class State(metaclass=ABCMeta):

      @property
      @abstractmethod
      def size(self) -> Tuple:
          ...

class Action(metaclass=ABCMeta):

      @property
      @abstractmethod
      def size(self) -> int:
          ...

class Environment(metaclass=ABCMeta):

      @abstractmethod
      def make(self) -> Any:
          ...
     
      @astractmethod
      def reset(self) -> np.ndarray:
          ...

      @abstractmethod
      def step(self, action: Any) -> Sequence[np.ndarray, float, bool, Dict]:
          ...

      @abstractmethod
      def render(self) -> np.ndarray:
          ...
 
      @property
      @abstractmethod
      def state(self) -> State:
          ...

      @property
      @abstractmethod
      def action(self) -> Action:
          ...
