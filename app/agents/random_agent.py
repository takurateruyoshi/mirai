import random
import numpy as np
from app.agents.base import BaseAgent

class RandomAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="RandomAgent")

    def get_action(self, board: np.ndarray, valid_moves: list) -> int:
        if not valid_moves:
            raise ValueError("No valid moves available.")
        return random.choice(valid_moves)