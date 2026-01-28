import time
from app.core.game import Connect4Game, Player
from app.agents.random_agent import RandomAgent
from app.agents.minimax_agent import MinimaxAgent

def run_console_simulation(rows=6, cols=7, delay=0.5):
    print(f"=== Starting Simulation: Board {rows}x{cols} ===")
    
    game = Connect4Game(rows=rows, cols=cols)
    
    # AIの設定
    agent1 = MinimaxAgent(depth=4)
    agent2 = RandomAgent()
    
    print(f"P1 (X): {agent1.name}")
    print(f"P2 (O): {agent2.name}")
    
    game.render()
    
    step_count = 0
    
    # ここは念のため残しておきますが、内部のbreakがメインの脱出条件になります
    while not game.is_terminal:
        step_count += 1
        current_player_symbol = "X (P1)" if game.current_player == Player.P1 else "O (P2)"
        print(f"\nTurn {step_count}: {current_player_symbol}")
        
        valid_moves = game.get_valid_moves()
        
        # --- 安全策: もし有効な手がない場合はループを抜ける ---
        if not valid_moves:
            print("No valid moves left.")
            break
            
        # エージェントに行動を選択させる
        if game.current_player == Player.P1:
            print("Thinking...")
            action = agent1.get_action(game.board, valid_moves)
        else:
            action = agent2.get_action(game.board, valid_moves)
            
        print(f"Selected Column: {action}")
        
        # 行動を実行
        _, winner, is_done = game.step(action)
        game.render()
        
        # --- 【修正箇所】ゲーム終了フラグ(is_done)を確認して即座に終了 ---
        if is_done:
            print("Game ended inside the loop.") # デバッグ用表示（不要なら削除可）
            break
        
        # 視認用ウェイト (ゲーム続行中の場合のみ待機)
        time.sleep(delay)

    print("\n=== Game Over ===")
    # 勝者の判定ロジックはそのまま
    # (game.stepの返り値 winner を使っても良いですが、現状のままでも動作します)
    if winner == Player.P1:
        print(f"Winner: {agent1.name} (X)")
    elif winner == Player.P2:
        print(f"Winner: {agent2.name} (O)")
    else:
        print("Draw!")

if __name__ == "__main__":
    run_console_simulation(rows=6, cols=7, delay=0.3)