# ── 第一階段：安裝 Python 依賴 ────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# 僅複製 requirements 以利用 Docker layer cache
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── 第二階段：執行環境 ─────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# 複製已安裝的套件
COPY --from=builder /install /usr/local

# 複製後端原始碼
COPY backend/src ./src

# 複製設定檔（優先使用掛載的 config.yaml，沒有時 fallback 至範例）
COPY config.example.yaml ./config.example.yaml

# 非 root 使用者執行（安全強化）
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
