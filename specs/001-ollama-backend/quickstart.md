# 快速上手：啟用 Ollama 後端

**功能分支**：`001-ollama-backend`  
**適用對象**：開發者、系統管理員

---

## 前置條件

1. 已安裝並啟動 Ollama 服務  
   ```bash
   # macOS
   brew install ollama
   ollama serve
   ```

2. 已拉取 TranslateGemma 模型  
   ```bash
   ollama pull translategemma:4b
   ```

3. 後端服務已依 backend/README.md 完成安裝

---

## 步驟 1：修改 config.yaml

在現有 `config.yaml` 的 `model` 區段加入以下三行：

```yaml
model:
  # 新增：選擇推論後端（local 為現行預設，ollama 使用外部 Ollama 服務）
  backend: "ollama"

  # 新增（ollama 後端專用）：Ollama 服務位址
  ollama_base_url: "http://localhost:11434"

  # 新增（ollama 後端專用）：Ollama 中的模型名稱
  ollama_model: "translategemma:4b"

  # 以下為現有欄位，保留不動
  name: "4b"
  base_path: "models"
  device: "auto"
  dtype: "auto"
```

> 若 Ollama 執行於其他機器（例如 `192.168.1.10`），  
> 改為 `ollama_base_url: "http://192.168.1.10:11434"`

---

## 步驟 2：重啟後端服務

```bash
# 若使用 Docker/Podman Compose
podman compose restart backend
# 或直接執行
cd backend && uvicorn src.main:app --reload
```

---

## 步驟 3：驗證

```bash
curl http://localhost:8000/health
```

預期回應：
```json
{
  "status": "ok",
  "backend": "ollama",
  "model": "translategemma:4b",
  "ollama_url": "http://localhost:11434",
  "device": null,
  "resolved_device": null,
  "model_loaded": true
}
```

---

## 步驟 4：測試翻譯

```bash
curl -X POST http://localhost:8000/api/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, world!", "source_lang": "en", "target_lang": "zh-TW", "stream": false}'
```

---

## 切換回本地模型（local 後端）

將 `config.yaml` 中 `backend` 改回：

```yaml
model:
  backend: "local"
```

重啟後端，即恢復原本行程內載入模型的行為。

---

## 常見問題

| 問題 | 原因 | 解決方案 |
|------|------|---------|
| `status: error` | Ollama 服務未啟動 | 執行 `ollama serve` |
| `status: error` | 模型未拉取 | 執行 `ollama pull translategemma:4b` |
| 翻譯結果品質不佳 | Ollama Prompt 格式與 TranslateGemma chat template 相異 | 調整 `OllamaBackend._build_messages` 中的 system message |
| 翻譯超時 | `translation.timeout` 設定過短 | 增大 `config.yaml` 中 `translation.timeout` 值 |

---

## 開發環境執行測試

```bash
cd backend
# 確認虛擬環境存在（.venv）
source .venv/bin/activate

# 執行所有單元測試（含 OllamaBackend mock 測試）
pytest tests/unit/ -v

# 執行整合測試
pytest tests/integration/ -v
```
