from abc import ABC, abstractmethod
import numpy as np

class BaseAgent(ABC):
    def __init__(self, name: str = "BaseAgent"):
        self.name = name

    @abstractmethod
    def get_action(self, board: np.ndarray, valid_moves: list) -> int:
        """
        現在の盤面と合法手を受け取り、選択した列（int）を返す。
        """
        pass