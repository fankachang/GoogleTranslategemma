# build-backend.ps1
# 替代 podman-compose up，自動管理 pip-cache
#
# 使用方式：
#   .\build-backend.ps1           # GPU（CUDA 12.4，預設）
#   .\build-backend.ps1 -CPU      # CPU-only torch
#
# 流程：
#   pip-cache/ 有 wheel → 直接 build（離線安裝）
#   pip-cache/ 為空     → 先在 Linux 容器內下載 wheel 並存回 pip-cache/，再 build
#
# 為何在 Linux 容器內下載：
#   在 Windows 執行 pip download 只會下載 Windows wheel，
#   Linux 容器無法使用。改在 python:3.11-slim 容器內下載，
#   透過 volume mount 寫回 host pip-cache/，即可自動取得
#   正確平台的 wheel（含 uvloop 等 Linux-only 套件），
#   無需手動指定 --platform。

param(
    [switch]$CPU
)

$ErrorActionPreference = "Stop"

$cacheDir = Join-Path $PWD "backend\pip-cache"
$reqFile  = Join-Path $PWD "backend\requirements.txt"

# 1. 確保 pip-cache 目錄存在
if (-not (Test-Path $cacheDir)) {
    New-Item -ItemType Directory -Force $cacheDir | Out-Null
}

# 2. 若無 wheel，在 Linux 容器內下載（自動取得正確平台，結果寫回 host pip-cache/）
$wheels = Get-ChildItem $cacheDir -Filter "*.whl" -ErrorAction SilentlyContinue
if ($null -eq $wheels -or $wheels.Count -eq 0) {
    $variant    = if ($CPU) { "CPU-only" } else { "CUDA 12.4 GPU" }
    $torchIndex = if ($CPU) { "https://download.pytorch.org/whl/cpu" } else { "https://download.pytorch.org/whl/cu124" }

    Write-Host "pip-cache 為空，在 Linux 容器內下載 wheel（$variant）..." -ForegroundColor Yellow

    # sh 腳本：先下載 torch，再下載其餘依賴（排除 torch 避免衝突）
    $shScript = "set -e" +
                "; pip download torch" +
                " --index-url $torchIndex" +
                " --extra-index-url https://pypi.org/simple -d /pip-cache" +
                "; grep -vE '^\s*torch\s*$' /requirements.txt > /tmp/other.txt" +
                "; pip download -r /tmp/other.txt -d /pip-cache" +
                '; echo "完成：$(ls /pip-cache/*.whl | wc -l) 個 wheel"'

    podman run --rm `
        -v "${cacheDir}:/pip-cache" `
        -v "${reqFile}:/requirements.txt:ro" `
        python:3.11-slim `
        sh -c $shScript

    if ($LASTEXITCODE -ne 0) {
        Write-Host "wheel 下載失敗，請確認網路連線後重試" -ForegroundColor Red
        exit 1
    }
    Write-Host "pip-cache 已儲存 $((Get-ChildItem $cacheDir -Filter '*.whl').Count) 個 wheel，下次 build 將離線使用" -ForegroundColor Green
} else {
    Write-Host "pip-cache 已有 $($wheels.Count) 個 wheel，跳過下載" -ForegroundColor Green
}

# 3. 啟動服務（build + up）
Write-Host "啟動服務..." -ForegroundColor Cyan
if ($CPU) {
    podman-compose up -d
} else {
    podman-compose -f docker-compose.yaml -f docker-compose.gpu.yaml up -d
}
