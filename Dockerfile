FROM python:3.10-slim

# 標準出力のバッファリングを無効化
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 依存関係のインストール（前回のタイムアウト対策も含めて記述しておきます）
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# --- 【重要】本番環境用にソースコードをコンテナ内にコピーする ---
COPY . .
# -------------------------------------------------------

# 起動コマンドの調整
# フォルダ構成によって書き方が変わります（後述の注意点を確認してください）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]