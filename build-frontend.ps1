# build-frontend.ps1
# 在本機預下載 NuGet 套件後建置前端 Container Image
#
# 使用方式：
#   .\build-frontend.ps1           # 建置前端 Container
#
# 流程：
#   nuget-cache/ 有套件 → 直接 build（離線安裝）
#   nuget-cache/ 為空   → 先在本機執行 dotnet restore 下載套件，再 build
#
# 為何在 Windows 可直接下載：
#   NuGet 套件為純 .NET managed code，不像 Python wheel 有平台差異，
#   在 Windows 下載的套件可直接供 Linux 容器使用。

$ErrorActionPreference = "Stop"

$nugetCacheDir = Join-Path $PWD "frontend\nuget-cache"
$frontendDir   = Join-Path $PWD "frontend"

# 1. 確保 nuget-cache 目錄存在
if (-not (Test-Path $nugetCacheDir)) {
    New-Item -ItemType Directory -Force $nugetCacheDir | Out-Null
}

# 2. 若無套件，在本機執行 dotnet restore 下載（NuGet 套件跨平台，無需 Linux 容器）
$nupkgs = Get-ChildItem $nugetCacheDir -Recurse -Include "*.nupkg" -ErrorAction SilentlyContinue
if ($null -eq $nupkgs -or $nupkgs.Count -eq 0) {
    Write-Host "nuget-cache 為空，在本機下載 NuGet 套件..." -ForegroundColor Yellow

    Push-Location $frontendDir
    try {
        dotnet restore --packages .\nuget-cache
        if ($LASTEXITCODE -ne 0) {
            Write-Host "NuGet 套件下載失敗，請確認網路連線後重試" -ForegroundColor Red
            exit 1
        }
    } finally {
        Pop-Location
    }

    $count = (Get-ChildItem $nugetCacheDir -Recurse -Include "*.nupkg").Count
    Write-Host "nuget-cache 已儲存 $count 個套件，下次 build 將離線使用" -ForegroundColor Green
} else {
    Write-Host "nuget-cache 已有 $($nupkgs.Count) 個套件，跳過下載" -ForegroundColor Green
}

# 3. 建置前端 Container Image
Write-Host "建置前端 Container Image..." -ForegroundColor Cyan
# Use Cache
# podman build -t frontend:latest $frontendDir
# Not Use Cache
podman build --no-cache -t frontend:latest $frontendDir

if ($LASTEXITCODE -ne 0) {
    Write-Host "Container build 失敗" -ForegroundColor Red
    exit 1
}

Write-Host "前端 Container Image 建置完成" -ForegroundColor Green
