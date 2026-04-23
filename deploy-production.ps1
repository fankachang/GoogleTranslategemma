# deploy-production.ps1
# 正式部署一鍵腳本：建置前端、啟動服務、健康檢查
#
# 使用方式：
#   .\deploy-production.ps1                  # 預設 GPU 模式（Windows + NVIDIA）
#   .\deploy-production.ps1 -CPU             # CPU 模式
#   .\deploy-production.ps1 -BackendUrl "http://10.1.1.99:8000"
#   .\deploy-production.ps1 -SkipFrontendBuild
#
# 注意：
#   1) 若使用 GPU，請先完成 NVIDIA Container Toolkit/CDI 設定。
#   2) 本腳本預設使用 Podman/Podman Compose。

param(
    [switch]$CPU,
    [string]$BackendUrl,
    [switch]$SkipFrontendBuild,
    [switch]$SkipHealthCheck,
    [int]$HealthTimeoutSec = 300
)

$ErrorActionPreference = "Stop"

function Test-HttpEndpoint {
    param(
        [Parameter(Mandatory = $true)][string]$Url,
        [Parameter(Mandatory = $true)][int]$TimeoutSec,
        [string]$Name = "service"
    )

    $start = Get-Date
    while (((Get-Date) - $start).TotalSeconds -lt $TimeoutSec) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                Write-Host "$Name 健康檢查成功：$Url (HTTP $($response.StatusCode))" -ForegroundColor Green
                return $true
            }
        } catch {
            # 等待服務啟動中
        }
        Start-Sleep -Seconds 2
    }

    Write-Host "$Name 健康檢查逾時：$Url" -ForegroundColor Red
    return $false
}

if (-not [string]::IsNullOrWhiteSpace($BackendUrl)) {
    $env:BACKEND_URL = $BackendUrl
    Write-Host "已設定 BACKEND_URL=$BackendUrl（僅本次執行有效）" -ForegroundColor Yellow
}

if (-not $SkipFrontendBuild) {
    Write-Host "[1/3] 建置前端映像檔..." -ForegroundColor Cyan
    & .\build-frontend.ps1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "build-frontend.ps1 執行失敗" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[1/3] 已略過前端建置" -ForegroundColor Yellow
}

Write-Host "[2/3] 啟動服務（backend + frontend）..." -ForegroundColor Cyan
if ($CPU) {
    & .\build-backend.ps1 -CPU
} else {
    & .\build-backend.ps1
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "build-backend.ps1 執行失敗" -ForegroundColor Red
    exit 1
}

if ($SkipHealthCheck) {
    Write-Host "[3/3] 已略過健康檢查" -ForegroundColor Yellow
    exit 0
}

Write-Host "[3/3] 執行健康檢查..." -ForegroundColor Cyan
$backendReady = Test-HttpEndpoint -Name "Backend" -Url "http://localhost:8000/health" -TimeoutSec $HealthTimeoutSec
$frontendReady = Test-HttpEndpoint -Name "Frontend" -Url "http://localhost:5000/" -TimeoutSec $HealthTimeoutSec

if (-not $backendReady -or -not $frontendReady) {
    Write-Host "部署完成，但健康檢查失敗，請執行 podman ps 與 podman logs <container> 進一步排查。" -ForegroundColor Red
    exit 1
}

Write-Host "部署完成：Frontend=http://localhost:5000, Backend=http://localhost:8000" -ForegroundColor Green
