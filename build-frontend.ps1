# build-frontend.ps1
# 在本機預下載 NuGet 套件後建置前端 Container Image
#
# 使用方式：
#   .\build-frontend.ps1           # 建置前端 Container
#
# 流程：
#   nuget-cache/ 有套件 → 直接 build（離線安裝）
#   nuget-cache/ 為空   → 使用容器內 SDK 執行 dotnet restore 下載套件，再 build
#
# 為何用容器執行 restore：
#   確保 NuGet 套件版本與容器內 SDK 版本完全一致，避免版本不符的建置錯誤。

$ErrorActionPreference = "Stop"

$nugetCacheDir = Join-Path $PWD "frontend\nuget-cache"
$frontendDir   = Join-Path $PWD "frontend"

# 1. 確保 nuget-cache 目錄存在
if (-not (Test-Path $nugetCacheDir)) {
    New-Item -ItemType Directory -Force $nugetCacheDir | Out-Null
}

# 2. 若無套件，用容器內 SDK 執行 restore，確保版本與 build 時一致
$nupkgs = Get-ChildItem $nugetCacheDir -Recurse -Include "*.nupkg" -ErrorAction SilentlyContinue
if ($null -eq $nupkgs -or $nupkgs.Count -eq 0) {
    Write-Host "nuget-cache 為空，使用容器 SDK 下載 NuGet 套件..." -ForegroundColor Yellow

    # 將 frontend/ 掛載進容器，用與 build 相同的 SDK 執行 restore
    # 輸出至 /nuget-cache（對應本機 nuget-cache/）
    podman run --rm `
        -v "${frontendDir}:/src" `
        mcr.microsoft.com/dotnet/sdk:9.0 `
        dotnet restore /src/frontend.csproj --packages /src/nuget-cache

    if ($LASTEXITCODE -ne 0) {
        Write-Host "NuGet 套件下載失敗，請確認網路連線後重試" -ForegroundColor Red
        exit 1
    }

    $count = (Get-ChildItem $nugetCacheDir -Recurse -Include "*.nupkg").Count
    Write-Host "nuget-cache 已儲存 $count 個套件，下次 build 將離線使用" -ForegroundColor Green
} else {
    Write-Host "nuget-cache 已有 $($nupkgs.Count) 個套件，跳過下載" -ForegroundColor Green
}

# 3. 建置前端 Container Image
Write-Host "建置前端 Container Image..." -ForegroundColor Cyan
podman build --no-cache -t frontend:latest $frontendDir

if ($LASTEXITCODE -ne 0) {
    Write-Host "Container build 失敗" -ForegroundColor Red
    exit 1
}

Write-Host "前端 Container Image 建置完成" -ForegroundColor Green
