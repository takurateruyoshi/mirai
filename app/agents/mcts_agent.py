import numpy as np
import math
import random
import copy
from app.agents.base import BaseAgent
from app.core.game import Connect4Game, Player

class MCTSNode:
    def __init__(self, state, parent=None, action=None):
        self.state = state  # 盤面の状態 (np.ndarray)
        self.parent = parent
        self.action = action  # このノードに到達するために打った手
        self.children = []
        self.visits = 0
        self.value = 0  # 勝利: +1, 敗北: -1, 引き分け: 0
        self.untried_actions = self._get_legal_actions(state)

    def _get_legal_actions(self, board):
        """盤面から合法手（列番号）のリストを取得"""
        return [c for c in range(board.shape[1]) if board[0][c] == 0]

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def best_child(self, c_param=1.414):
        """UCB1スコアに基づいて最も有望な子ノードを選択"""
        choices_weights = [
            (child.value / child.visits) + c_param * math.sqrt((2 * math.log(self.visits) / child.visits))
            for child in self.children
        ]
        return self.children[np.argmax(choices_weights)]

class MCTSAgent(BaseAgent):
    def __init__(self, simulation_limit=1000):
        """
        simulation_limit: 1手を選択するために行うシミュレーション回数
        """
        super().__init__(name=f"MCTS(sims={simulation_limit})")
        self.simulation_limit = simulation_limit

    def get_action(self, board: np.ndarray, valid_moves: list) -> int:
        # ルートノードの作成
        root = MCTSNode(state=board.copy())
        
        # プレイヤーの特定（現在の手番）
        # Connect4Gameロジックでは、手番プレイヤーはboardからは自明ではないため、
        # 盤面の駒数をカウントして推定します（先攻P1=1, 後攻P2=-1）
        p1_pieces = np.sum(board == Player.P1)
        p2_pieces = np.sum(board == Player.P2)
        current_player = Player.P1 if p1_pieces == p2_pieces else Player.P2

        for _ in range(self.simulation_limit):
            node = self._tree_policy(root, current_player)
            reward = self._default_policy(node.state, current_player) # シミュレーション実行
            self._backup(node, reward)

        # 最も訪問回数が多い手を選択（頑健な選択）
        best_child_node = root.best_child(c_param=0) # 探索項なしで純粋な評価
        return best_child_node.action

    def _tree_policy(self, node: MCTSNode, root_player):
        """
        Selection & Expansion:
        未展開の行動があれば展開し、そうでなければUCBに従って子を選択して降りる。
        """
        current_player = root_player
        
        # 深さを追跡してプレイヤーを切り替える必要があるが、
        # 簡易的にノードの深さで判定
        
        while not self._is_terminal(node.state):
            if not node.is_fully_expanded():
                return self._expand(node)
            else:
                node = node.best_child()
        return node

    def _expand(self, node: MCTSNode):
        action = node.untried_actions.pop()
        next_state = self._get_next_state(node.state, action)
        child_node = MCTSNode(next_state, parent=node, action=action)
        node.children.append(child_node)
        return child_node

    def _default_policy(self, state: np.ndarray, root_player):
        """
        Simulation (Rollout):
        ゲーム終了までランダムに手を打ち続ける。
        Rootプレイヤーが勝てば +1, 負ければ -1
        """
        current_state = state.copy()
        
        # 現在の盤面での手番を推定
        p1_c = np.sum(current_state == Player.P1)
        p2_c = np.sum(current_state == Player.P2)
        current_player = Player.P1 if p1_c == p2_c else Player.P2

        # ゲーム終了までループ
        while True:
            if self._check_win(current_state, Player.P1):
                return 1 if root_player == Player.P1 else -1
            if self._check_win(current_state, Player.P2):
                return 1 if root_player == Player.P2 else -1
            
            valid_moves = [c for c in range(current_state.shape[1]) if current_state[0][c] == 0]
            if not valid_moves:
                return 0 # Draw
            
            # ランダムに行動
            action = random.choice(valid_moves)
            self._apply_move(current_state, action, current_player)
            
            # プレイヤー交代
            current_player = Player.P2 if current_player == Player.P1 else Player.P1

    def _backup(self, node: MCTSNode, reward):
        """Backpropagation"""
        while node is not None:
            node.visits += 1
            # 階層ごとに手番が入れ替わるため、報酬の視点を反転させる
            # ノードの親から見て、その手が良かったかどうか
            node.value += reward
            reward = -reward # 相手にとっての報酬は逆になる
            node = node.parent

    # --- Utility Functions (Lightweight Game Logic for Speed) ---
    # Gameクラスを直接使うと重いので、Numpy操作だけで完結させる

    def _get_next_state(self, board, action):
        next_board = board.copy()
        p1_c = np.sum(board == Player.P1)
        p2_c = np.sum(board == Player.P2)
        player = Player.P1 if p1_c == p2_c else Player.P2
        self._apply_move(next_board, action, player)
        return next_board

    def _apply_move(self, board, col, player):
        for r in range(board.shape[0] - 1, -1, -1):
            if board[r][col] == 0:
                board[r][col] = player
                return

    def _is_terminal(self, board):
        return self._check_win(board, Player.P1) or \
               self._check_win(board, Player.P2) or \
               len([c for c in range(board.shape[1]) if board[0][c] == 0]) == 0

    def _check_win(self, board, player):
        # game.pyのロジックを高速化のために流用推奨
        # ここでは実装簡略化のため、game.pyと同じロジックが必要
        rows, cols = board.shape
        # Horizontal
        for r in range(rows):
            for c in range(cols - 3):
                if np.all(board[r, c:c+4] == player): return True
        # Vertical
        for r in range(rows - 3):
            for c in range(cols):
                if np.all(board[r:r+4, c] == player): return True
        # Diagonals
        for r in range(rows - 3):
            for c in range(cols - 3):
                if all(board[r+i][c+i] == player for i in range(4)): return True
        for r in range(rows - 3):
            for c in range(3, cols):
                if all(board[r+i][c-i] == player for i in range(4)): return True
        return False