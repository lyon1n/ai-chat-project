# 启动本机服务 + Cloudflare 快速隧道（无需绑卡）
# 用法：在项目根目录执行  .\scripts\start-cloudflare.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

# 查找 cloudflared
$cf = (Get-Command cloudflared -ErrorAction SilentlyContinue)?.Source
if (-not $cf) {
    $cf = "$env:ProgramFiles\Cloudflare\cloudflared\cloudflared.exe"
}
if (-not (Test-Path $cf)) {
    $cf = "${env:ProgramFiles(x86)}\cloudflared\cloudflared.exe"
}
if (-not (Test-Path $cf)) {
    Write-Host "未找到 cloudflared，正在安装..."
    winget install Cloudflare.cloudflared -e --accept-source-agreements --accept-package-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    $cf = (Get-Command cloudflared -ErrorAction SilentlyContinue)?.Source
}
if (-not $cf -or -not (Test-Path $cf)) {
    Write-Host "安装失败。请手动安装: winget install Cloudflare.cloudflared"
    exit 1
}

# 确保有 static 前端
if (-not (Test-Path "$Root\static\index.html")) {
    Write-Host ">> 首次运行，构建前端..."
    & "$Root\scripts\build-static.ps1"
}

Write-Host ""
Write-Host "=========================================="
Write-Host "  启动后端 (端口 8000)..."
Write-Host "=========================================="

$venvPython = "$Root\venv\Scripts\python.exe"
$python = if (Test-Path $venvPython) { $venvPython } else { "python" }

Start-Process -FilePath $python -ArgumentList "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000" `
    -WorkingDirectory $Root -WindowStyle Minimized

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "=========================================="
Write-Host "  启动 Cloudflare 隧道..."
Write-Host "  下面会出现你的公网地址 (https://xxx.trycloudflare.com)"
Write-Host "  复制该地址，发给任何人即可访问"
Write-Host "  按 Ctrl+C 停止"
Write-Host "=========================================="
Write-Host ""

& $cf tunnel --url http://127.0.0.1:8000
