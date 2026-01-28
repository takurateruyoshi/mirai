import uuid
import numpy as np
from typing import Dict, Optional

from app.core.game import Connect4Game, Player
from app.agents.base import BaseAgent
from app.agents.random_agent import RandomAgent
from app.agents.minimax_agent import MinimaxAgent
from app.agents.mcts_agent import MCTSAgent
from app.schemas import GameConfig, AgentType

class GameManager:
    def __init__(self):
        # メモリ上でゲームセッションを保持 (再起動で消えます)
        self.games: Dict[str, Connect4Game] = {}
        self.agents: Dict[str, Dict[int, BaseAgent]] = {}

    def create_game(self, config: GameConfig) -> str:
        game_id = str(uuid.uuid4())
        game = Connect4Game(rows=config.rows, cols=config.cols)
        self.games[game_id] = game
        
        # エージェントのセットアップ
        self.agents[game_id] = {}
        self._setup_agent(game_id, Player.P1, config.p1_agent, config)
        self._setup_agent(game_id, Player.P2, config.p2_agent, config)
        
        return game_id

    def _setup_agent(self, game_id: str, player: int, agent_type: AgentType, config: GameConfig):
        if agent_type == AgentType.HUMAN:
            return # Humanはエージェントインスタンスを持たない

        agent = None
        if agent_type == AgentType.RANDOM:
            agent = RandomAgent()
        elif agent_type == AgentType.MINIMAX:
            agent = MinimaxAgent(depth=config.minimax_depth)
        elif agent_type == AgentType.MCTS:
            agent = MCTSAgent(simulation_limit=config.mcts_simulations)
        
        if agent:
            self.agents[game_id][player] = agent

    def get_game(self, game_id: str) -> Optional[Connect4Game]:
        return self.games.get(game_id)

    def get_agent(self, game_id: str, player: int) -> Optional[BaseAgent]:
        return self.agents.get(game_id, {}).get(player)

    def delete_game(self, game_id: str):
        if game_id in self.games:
            del self.games[game_id]
        if game_id in self.agents:
            del self.agents[game_id]

# シングルトンとしてインスタンス化
game_manager = GameManager()