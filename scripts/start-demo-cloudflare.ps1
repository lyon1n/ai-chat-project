# 本地公网演示：后端 + 前端 + Cloudflare Tunnel
# 运行前准备：
# 1. 填好项目根目录 .env 中的 DEEPSEEK_API_KEY
# 2. 安装 cloudflared：https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
# 3. 在 PowerShell 执行：powershell -ExecutionPolicy Bypass -File scripts/start-demo-cloudflare.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

function Stop-Port($port) {
    Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | ForEach-Object {
        $procId = $_.OwningProcess
        if ($procId) {
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        }
    }
}

function Assert-Command($name, $installHint) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
        Write-Host "未找到 $name"
        Write-Host $installHint
        exit 1
    }
}

Write-Host ""
Write-Host "=========================================="
Write-Host "  AI 知识库聊天 - Cloudflare Tunnel 演示"
Write-Host "=========================================="
Write-Host ""

Assert-Command "cloudflared" "请先安装 cloudflared，然后重新运行本脚本。"

$venvPython = "$Root\venv\Scripts\python.exe"
$venvPip = "$Root\venv\Scripts\pip.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host ">> 创建 Python 虚拟环境..."
    python -m venv venv
}

if (-not (Test-Path "$Root\.env")) {
    Copy-Item "$Root\.env.example" "$Root\.env"
    Write-Host ">> 已创建 .env，请填写 DEEPSEEK_API_KEY 后重新运行"
    exit 1
}

Write-Host ">> 安装后端依赖..."
& $venvPip install -r "$Root\requirements.txt" -q

if (-not (Test-Path "$Root\frontend\node_modules")) {
    Write-Host ">> 安装前端依赖..."
    Set-Location "$Root\frontend"
    npm install
    Set-Location $Root
}

Stop-Port 8000
Stop-Port 5173
Start-Sleep -Seconds 1

$env:USE_SQLITE = "true"

Write-Host ">> 启动后端 http://127.0.0.1:8000 ..."
Start-Process -FilePath $venvPython -ArgumentList "-m", "uvicorn", "backend.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000" `
    -WorkingDirectory $Root -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host ">> 启动前端 http://127.0.0.1:5173 ..."
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "cd /d `"$Root\frontend`" && npm run dev" -WindowStyle Normal

Start-Sleep -Seconds 4

try {
    $health = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 8
    Write-Host "后端 OK: $($health.Content)"
} catch {
    Write-Host "警告：后端尚未就绪，请查看后端窗口是否有报错"
}

Write-Host ""
Write-Host ">> 即将启动 Cloudflare Tunnel"
Write-Host ">> 复制终端中出现的 https://*.trycloudflare.com 链接用于演示"
Write-Host ">> 关闭本窗口会停止公网访问"
Write-Host ""

cloudflared tunnel --url http://127.0.0.1:5173
