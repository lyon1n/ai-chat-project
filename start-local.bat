@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo ===== AI 知识库聊天 - 本地启动 =====
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start-local.ps1"
echo.
pause
