let currentGameId = null;
let gameState = null;
let config = {};
let aiTurnTimeout = null; // 【追加】タイマーIDを保持する変数

const API_BASE = ""; 

// DOM要素
const boardContainer = document.getElementById('board-container');
const statusDiv = document.getElementById('game-status');

// 【追加】ゲームの状態を完全にリセットする関数
function resetGameState() {
    // 1. 待機中のAIのターンがあればキャンセル
    if (aiTurnTimeout) {
        clearTimeout(aiTurnTimeout);
        aiTurnTimeout = null;
    }
    // 2. IDを無効化（通信中の処理が戻ってきたときに無視させるため）
    currentGameId = null;
    gameState = null;
    statusDiv.innerText = "Resetting...";
}

async function startGame() {
    resetGameState();
    statusDiv.innerText = "Starting game...";
    
    // --- 【修正箇所】プルダウンから行・列を同時に取得する処理 ---
    const sizeSelect = document.getElementById('board-size');
    const sizeValue = sizeSelect.value.split(','); // "6,7" を ["6", "7"] に分割
    
    const selectedRows = parseInt(sizeValue[0]);
    const selectedCols = parseInt(sizeValue[1]);
    
    config = {
        rows: selectedRows,
        cols: selectedCols,
        p1_agent: document.getElementById('p1-agent').value,
        p2_agent: document.getElementById('p2-agent').value,
        minimax_depth: 4,
        mcts_simulations: 1000
    };

    try {
        const response = await fetch(`${API_BASE}/games/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        
        const newGameState = await response.json();
        
        // ここで正式に新しいIDをセット
        gameState = newGameState;
        currentGameId = gameState.game_id;
        
        renderBoard();
        checkNextTurn();
    } catch (error) {
        statusDiv.innerText = "Error starting game: " + error;
    }
}

async function makeHumanMove(col) {
    if (!currentGameId || gameState.is_terminal) return;
    
    // 【追加】クリックした瞬間のIDを保存（念のため）
    const myGameId = currentGameId;

    const currentPlayerAgent = gameState.current_player === 1 ? config.p1_agent : config.p2_agent;
    if (currentPlayerAgent !== 'human') return;

    try {
        const response = await fetch(`${API_BASE}/games/${currentGameId}/move`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ column: col })
        });
        if (!response.ok) throw new Error(await response.text());
        
        // 【追加】通信中にゲームがリセットされていたら何もしない
        if (currentGameId !== myGameId) return;

        gameState = await response.json();
        renderBoard();
        checkNextTurn();
    } catch (error) {
        console.error("Move error:", error);
    }
}

async function triggerAIMove() {
    // 【追加】この関数が呼ばれた時点のGameIDを記憶
    const myGameId = currentGameId;

    if (!myGameId || (gameState && gameState.is_terminal)) return;
    
    statusDiv.innerHTML = `AI (Player ${gameState.current_player === 1 ? '1' : '2'}) is thinking... <span class="thinking">●</span>`;
    
    // ウェイト
    await new Promise(r => setTimeout(r, 500));

    // 【追加】ウェイト中に再スタートされていたらここで中断
    if (currentGameId !== myGameId) return;

    try {
        const response = await fetch(`${API_BASE}/games/${myGameId}/ai-move`, {
            method: 'POST'
        });
        
        // 【重要】AI思考中に「Start Game」が押された場合、
        // currentGameId は null か新しいIDになっているため、ここで不一致が起きる
        if (currentGameId !== myGameId) {
            console.log("Game reset during AI move. Ignoring result.");
            return;
        }

        gameState = await response.json();
        renderBoard();
        checkNextTurn();
    } catch (error) {
        // エラー発生時も、ゲームが変わっていたらエラー表示しない
        if (currentGameId === myGameId) {
            statusDiv.innerText = "AI Error: " + error;
        }
    }
}

function checkNextTurn() {
    // そもそもゲームIDが無い（リセット直後）なら何もしない
    if (!currentGameId) return;

    if (gameState.is_terminal) {
        statusDiv.innerText = gameState.message;
        boardContainer.classList.add('game-over');
        return;
    }

    const currentPlayer = gameState.current_player;
    const agentType = currentPlayer === 1 ? config.p1_agent : config.p2_agent;
    const playerName = currentPlayer === 1 ? "Player 1 (X)" : "Player 2 (O)";

    statusDiv.innerText = `${playerName}'s Turn (${agentType})`;

    if (agentType !== 'human') {
        // AIの手番
        // 【修正】setTimeoutのIDを変数に保存し、リセット可能にする
        if (aiTurnTimeout) clearTimeout(aiTurnTimeout);
        aiTurnTimeout = setTimeout(triggerAIMove, 100); 
    } else {
        // 人間の手番
        boardContainer.classList.remove('game-over');
    }
}

function renderBoard() {
    // リセット直後などGameStateがない場合は描画しない
    if (!gameState || !gameState.board) return;

    boardContainer.innerHTML = '';
    const board = gameState.board;
    const rows = board.length;
    const cols = board[0].length;

    const boardDiv = document.createElement('div');
    boardDiv.id = 'board';
    
    const currentPlayerAgent = gameState.current_player === 1 ? config.p1_agent : config.p2_agent;
    if (currentPlayerAgent === 'human' && !gameState.is_terminal) {
        boardDiv.classList.add('human-turn');
    }

    for (let r = 0; r < rows; r++) {
        const rowDiv = document.createElement('div');
        rowDiv.className = 'board-row';
        for (let c = 0; c < cols; c++) {
            const cellDiv = document.createElement('div');
            cellDiv.className = 'cell';
            cellDiv.dataset.row = r;
            cellDiv.dataset.col = c;
            cellDiv.dataset.value = board[r][c];

            const tokenDiv = document.createElement('div');
            tokenDiv.className = 'token';
            cellDiv.appendChild(tokenDiv);

            if (r === 0) {
                // ここでも念のためIDチェックを入れるラッパー経由でも良いが
                // makeHumanMove内でチェックしているのでそのままでOK
                cellDiv.onclick = () => makeHumanMove(c);
            }
            rowDiv.appendChild(cellDiv);
        }
        boardDiv.appendChild(rowDiv);
    }
    boardContainer.appendChild(boardDiv);
}