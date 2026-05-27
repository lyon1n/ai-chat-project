# 本地开发：后端 + 前端
# 用法：双击 start-local.bat

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
Set-Location $Root

Write-Host ""
Write-Host "=========================================="
Write-Host "  AI 知识库聊天 - 本地开发"
Write-Host "=========================================="
Write-Host ""

$venvPython = "$Root\venv\Scripts\python.exe"
$venvPip = "$Root\venv\Scripts\pip.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host ">> 创建虚拟环境..."
    python -m venv venv
}

Write-Host ">> 安装后端依赖..."
& $venvPip install -r "$Root\requirements.txt" -q

if (-not (Test-Path "$Root\.env")) {
    Copy-Item "$Root\.env.example" "$Root\.env"
    Write-Host ">> 已创建 .env，请填写 DEEPSEEK_API_KEY 后重新运行"
    Read-Host "按 Enter 退出"
    exit 1
}

if (-not (Test-Path "$Root\frontend\node_modules")) {
    Write-Host ">> 安装前端依赖..."
    Set-Location "$Root\frontend"
    npm install
    Set-Location $Root
}

function Stop-Port($port) {
    Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | ForEach-Object {
        $procId = $_.OwningProcess
        if ($procId) {
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        }
    }
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
Write-Host "=========================================="
Write-Host "  在浏览器打开: http://127.0.0.1:5173"
Write-Host "  关闭两个命令行窗口即可停止"
Write-Host "=========================================="
Write-Host ""

Start-Process "http://127.0.0.1:5173"
