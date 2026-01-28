from pydantic import BaseModel
from typing import List, Optional, Literal
from enum import Enum

class AgentType(str, Enum):
    HUMAN = "human"
    RANDOM = "random"
    MINIMAX = "minimax"
    MCTS = "mcts"

class GameConfig(BaseModel):
    rows: int = 6
    cols: int = 7
    p1_agent: AgentType = AgentType.HUMAN
    p2_agent: AgentType = AgentType.RANDOM
    
    # AI設定用パラメータ（オプション）
    minimax_depth: int = 4
    mcts_simulations: int = 1000

class MoveRequest(BaseModel):
    column: int

class GameState(BaseModel):
    game_id: str
    board: List[List[int]]  # Numpy配列はJSON化できないためリスト変換
    current_player: int     # 1 or -1
    winner: Optional[int]
    is_terminal: bool
    last_move: Optional[int] = None
    message: str