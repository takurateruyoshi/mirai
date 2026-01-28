import numpy as np
from enum import Enum
from typing import List, Tuple, Optional

class Player(int, Enum):
    EMPTY = 0
    P1 = 1  # 先攻
    P2 = -1 # 後攻

class Connect4Game:
    def __init__(self, rows: int = 6, cols: int = 7):
        self.rows = rows
        self.cols = cols
        self.board = np.zeros((rows, cols), dtype=int)
        self.current_player = Player.P1
        self.winner = None
        self.is_terminal = False

    def reset(self):
        self.board = np.zeros((self.rows, self.cols), dtype=int)
        self.current_player = Player.P1
        self.winner = None
        self.is_terminal = False
        return self.board

    def get_valid_moves(self) -> List[int]:
        """一番上の行が空いている列（インデックス）のリストを返す"""
        if self.is_terminal:
            return []
        # 0行目（一番上）が0（空）である列を探す
        return [c for c in range(self.cols) if self.board[0][c] == Player.EMPTY]

    def step(self, col: int) -> Tuple[np.ndarray, Optional[Player], bool]:
        """
        行動を実行し、(次状態, 勝者, 終了フラグ) を返す
        """
        if col not in self.get_valid_moves():
            raise ValueError(f"Invalid move: Column {col} is full or out of bounds.")

        # 重力の実装：一番下の空いている行を探す
        for r in range(self.rows - 1, -1, -1):
            if self.board[r][col] == Player.EMPTY:
                self.board[r][col] = self.current_player
                break

        # 勝敗判定
        if self.check_win(self.current_player):
            self.winner = self.current_player
            self.is_terminal = True
        elif len(self.get_valid_moves()) == 0:
            # 引き分け
            self.winner = None # None means draw if terminal is True
            self.is_terminal = True
        else:
            # プレイヤー交代
            self.current_player = Player.P2 if self.current_player == Player.P1 else Player.P1

        return self.board.copy(), self.winner, self.is_terminal

    def check_win(self, player: Player) -> bool:
        """指定されたプレイヤーが勝利条件（4つ並び）を満たしているか判定"""
        # 水平、垂直、対角線方向をチェック
        # Note: 可変サイズ対応のため汎用的なチェックを行います
        
        # 水平
        for r in range(self.rows):
            for c in range(self.cols - 3):
                if np.all(self.board[r, c:c+4] == player):
                    return True
        
        # 垂直
        for r in range(self.rows - 3):
            for c in range(self.cols):
                if np.all(self.board[r:r+4, c] == player):
                    return True
        
        # 右下がり対角線 (\)
        for r in range(self.rows - 3):
            for c in range(self.cols - 3):
                if all(self.board[r+i][c+i] == player for i in range(4)):
                    return True

        # 左下がり対角線 (/)
        for r in range(self.rows - 3):
            for c in range(3, self.cols):
                if all(self.board[r+i][c-i] == player for i in range(4)):
                    return True
        
        return False

    def render(self):
        """コンソールに盤面を表示"""
        print("\n  " + " ".join([str(i) for i in range(self.cols)]))
        for r in range(self.rows):
            row_str = "|"
            for c in range(self.cols):
                val = self.board[r][c]
                char = "."
                if val == Player.P1: char = "X"
                elif val == Player.P2: char = "O"
                row_str += f" {char}"
            print(row_str + " |")
        print("-" * (self.cols * 2 + 3))