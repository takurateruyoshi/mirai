from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # 追加
from fastapi.responses import FileResponse # 追加
import numpy as np
from app.schemas import GameConfig, GameState, MoveRequest
from app.managers import game_manager
from app.core.game import Player



app = FastAPI(title="Connect 4 AI Platform API")

# フロントエンド開発を見越してCORSを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイルのマウント (これを追加)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ルートアクセスでindex.htmlを返す (これを追加)
@app.get("/")
async def read_index():
    return FileResponse('app/static/index.html')

@app.post("/games/start", response_model=GameState)
def start_game(config: GameConfig):
    """新しいゲームセッションを作成します"""
    game_id = game_manager.create_game(config)
    game = game_manager.get_game(game_id)
    
    return GameState(
        game_id=game_id,
        board=game.board.tolist(),
        current_player=game.current_player,
        winner=game.winner,
        is_terminal=game.is_terminal,
        message="Game started"
    )

@app.get("/games/{game_id}", response_model=GameState)
def get_game_state(game_id: str):
    """現在の盤面状態を取得します"""
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    msg = "Game in progress"
    if game.is_terminal:
        if game.winner:
            msg = f"Winner: Player {1 if game.winner == 1 else 2}"
        else:
            msg = "Draw"

    return GameState(
        game_id=game_id,
        board=game.board.tolist(),
        current_player=game.current_player,
        winner=game.winner,
        is_terminal=game.is_terminal,
        message=msg
    )

@app.post("/games/{game_id}/move", response_model=GameState)
def make_move(game_id: str, move: MoveRequest):
    """人間プレイヤーが手を打ちます"""
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if game.is_terminal:
        raise HTTPException(status_code=400, detail="Game is already finished")

    # 現在の手番がAIの場合、人間が操作しようとしたらエラーにするなどの制御が可能ですが、
    # デバッグ用にここでは許可しておきます。

    try:
        game.step(move.column)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return get_game_state(game_id)

@app.post("/games/{game_id}/ai-move", response_model=GameState)
def trigger_ai_move(game_id: str):
    """現在の手番のAIに手を打たせます"""
    game = game_manager.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    if game.is_terminal:
        raise HTTPException(status_code=400, detail="Game is already finished")

    # 現在のプレイヤー用のエージェントを取得
    agent = game_manager.get_agent(game_id, game.current_player)
    if not agent:
        raise HTTPException(status_code=400, detail="Current player is not an AI agent")

    valid_moves = game.get_valid_moves()
    action = agent.get_action(game.board, valid_moves)
    
    game.step(action)
    
    # 応答に「AIがどこに打ったか」を含めるため、state取得時にlast_moveを入れられると良いですが、
    # 今回は盤面差分で判定します
    return get_game_state(game_id)

@app.delete("/games/{game_id}")
def delete_game(game_id: str):
    game_manager.delete_game(game_id)
    return {"message": "Game session deleted"}