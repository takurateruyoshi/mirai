FROM python:3.10-slim

# 標準出力のバッファリングを無効化（ログを即時表示）
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードはDocker Composeのボリュームマウントで同期するため
# ここではCOPYしない（本番ビルド時はCOPYする）

# デフォルトコマンド（FastAPIサーバー起動）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]