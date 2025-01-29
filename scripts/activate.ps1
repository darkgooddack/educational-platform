# Переходим в корневую директорию
Set-Location $PSScriptRoot/..

# Запускаем setup.ps1
./scripts/setup.ps1

# Запускаем dev режим из корня
Write-Host "🚀 Запускаю dev режим..." -ForegroundColor Cyan
uv run dev