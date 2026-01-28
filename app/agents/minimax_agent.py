import numpy as np
import random
import math
from app.agents.base import BaseAgent
from app.core.game import Player

class MinimaxAgent(BaseAgent):
    def __init__(self, depth: int = 4):
        super().__init__(name=f"Minimax(depth={depth})")
        self.depth = depth
        self.ROW_COUNT = 0
        self.COLUMN_COUNT = 0

    def get_action(self, board: np.ndarray, valid_moves: list) -> int:
        self.ROW_COUNT, self.COLUMN_COUNT = board.shape
        
        # アルファベータ法で探索を実行
        # alpha: maxプレイヤーが保証されている最小スコア
        # beta: minプレイヤーが保証されている最大スコア
        col, minimax_score = self.minimax(board, self.depth, -math.inf, math.inf, True)
        
        # 万が一有効な手が見つからない場合（通常はないが安全策）
        if col is None:
            col = random.choice(valid_moves)
            
        return col

    def minimax(self, board: np.ndarray, depth: int, alpha: float, beta: float, maximizingPlayer: bool):
        valid_locations = self.get_valid_locations(board)
        is_terminal = self.is_terminal_node(board)

        # ベースケース：深さ制限到達 または ゲーム終了
        if depth == 0 or is_terminal:
            if is_terminal:
                if self.check_win_static(board, Player.P1): # AI (Assume P1 is AI for simplicity logic here, adjusted below)
                    return (None, 10000000000000)
                elif self.check_win_static(board, Player.P2):
                    return (None, -10000000000000)
                else: # Draw
                    return (None, 0)
            else: # 深さ0
                return (None, self.score_position(board, Player.P1)) # AI視点のスコア

        if maximizingPlayer:
            value = -math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board, col)
                b_copy = board.copy()
                b_copy[row][col] = Player.P1 # AIの手をシミュレーション
                new_score = self.minimax(b_copy, depth - 1, alpha, beta, False)[1]
                
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break # Beta Cutoff
            return column, value

        else: # Minimizing Player (Opponent)
            value = math.inf
            column = random.choice(valid_locations)
            for col in valid_locations:
                row = self.get_next_open_row(board, col)
                b_copy = board.copy()
                b_copy[row][col] = Player.P2 # 相手の手をシミュレーション
                new_score = self.minimax(b_copy, depth - 1, alpha, beta, True)[1]
                
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break # Alpha Cutoff
            return column, value

    # --- Helper Functions ---

    def score_position(self, board: np.ndarray, piece: int) -> int:
        score = 0
        opp_piece = Player.P2 if piece == Player.P1 else Player.P1

        # Center Column Preference
        center_array = [int(i) for i in list(board[:, self.COLUMN_COUNT // 2])]
        center_count = center_array.count(piece)
        score += center_count * 3

        # Horizontal
        for r in range(self.ROW_COUNT):
            row_array = [int(i) for i in list(board[r, :])]
            for c in range(self.COLUMN_COUNT - 3):
                window = row_array[c:c+4]
                score += self.evaluate_window(window, piece, opp_piece)

        # Vertical
        for c in range(self.COLUMN_COUNT):
            col_array = [int(i) for i in list(board[:, c])]
            for r in range(self.ROW_COUNT - 3):
                window = col_array[r:r+4]
                score += self.evaluate_window(window, piece, opp_piece)

        # Positive Diagonal
        for r in range(self.ROW_COUNT - 3):
            for c in range(self.COLUMN_COUNT - 3):
                window = [board[r+i][c+i] for i in range(4)]
                score += self.evaluate_window(window, piece, opp_piece)

        # Negative Diagonal
        for r in range(self.ROW_COUNT - 3):
            for c in range(self.COLUMN_COUNT - 3):
                window = [board[r+3-i][c+i] for i in range(4)]
                score += self.evaluate_window(window, piece, opp_piece)

        return score

    def evaluate_window(self, window: list, piece: int, opp_piece: int) -> int:
        score = 0
        if window.count(piece) == 4:
            score += 100
        elif window.count(piece) == 3 and window.count(0) == 1:
            score += 5
        elif window.count(piece) == 2 and window.count(0) == 2:
            score += 2

        if window.count(opp_piece) == 3 and window.count(0) == 1:
            score -= 4 # 相手のリーチを阻止する優先度
        
        return score

    def get_valid_locations(self, board):
        valid = []
        for col in range(self.COLUMN_COUNT):
            if board[0][col] == 0:
                valid.append(col)
        return valid

    def get_next_open_row(self, board, col):
        for r in range(self.ROW_COUNT - 1, -1, -1):
            if board[r][col] == 0:
                return r
    
    def is_terminal_node(self, board):
        return self.check_win_static(board, Player.P1) or \
               self.check_win_static(board, Player.P2) or \
               len(self.get_valid_locations(board)) == 0

    def check_win_static(self, board, player):
        # Game.pyのロジックと同様だが、Boardインスタンスを持たないためstaticに再定義
        # (簡略化のためGame.pyからロジックを流用推奨だが、ここでは依存を減らすため記述)
        rows, cols = board.shape
        # Horizontal
        for c in range(cols-3):
            for r in range(rows):
                if board[r][c] == player and board[r][c+1] == player and board[r][c+2] == player and board[r][c+3] == player:
                    return True
        # Vertical
        for c in range(cols):
            for r in range(rows-3):
                if board[r][c] == player and board[r+1][c] == player and board[r+2][c] == player and board[r+3][c] == player:
                    return True
        # Diagonals
        for c in range(cols-3):
            for r in range(rows-3):
                if board[r][c] == player and board[r+1][c+1] == player and board[r+2][c+2] == player and board[r+3][c+3] == player:
                    return True
                if board[r+3][c] == player and board[r+2][c+1] == player and board[r+1][c+2] == player and board[r][c+3] == player:
                    return True
        return False