# 构建前端到 static/，供 uvicorn 同一端口提供网页+API
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host ">> 构建前端..."
Set-Location frontend
$env:VITE_API_URL = ""
npm run build

Set-Location ..
if (Test-Path static) { Remove-Item -Recurse -Force static }
Copy-Item -Recurse frontend\dist static

Write-Host ">> 完成。static/ 已就绪，运行 start-cloudflare.ps1 启动公网访问"
