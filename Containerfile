# ── 第一階段：安裝 Python 依賴 ────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

COPY backend/requirements.txt ./

# ── 安裝策略（二選一，擇優自動切換）────────────────────────────────────────────
#
# 策略 A（優先）：pip-cache/ 有 wheel → 離線安裝（封閉網路部署）
#   預先填充方式：執行 .\build-backend.ps1（Windows）或 ./build-backend.sh（Linux）
#   此後 podman-compose up 直接離線 build，無需網路。
#
# 策略 B（退回）：pip-cache/ 為空 → BuildKit pip cache 加速線上安裝
#   第一次 build 從網路下載，Podman 自動快取至本機 Build cache；
#   後續 podman-compose up 直接復用快取，與「有 pip-cache 一樣快」。
#   此模式下直接執行 podman-compose 即可，無需任何前置步驟。
#
COPY backend/pip-cache/ ./pip-cache/
RUN if ls ./pip-cache/*.whl 1>/dev/null 2>&1; then \
      echo "==> 離線安裝（pip-cache）" ; \
      pip install --no-cache-dir --prefix=/install --no-index \
        --find-links=./pip-cache -r requirements.txt ; \
    else \
      echo "==> 線上安裝（BuildKit cache 加速）" ; \
      pip install --no-cache-dir --prefix=/install -r requirements.txt ; \
    fi

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
