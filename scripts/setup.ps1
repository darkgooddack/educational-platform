# Устанавливаем uv если его нет
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "📥 Устанавливаю uv..." -ForegroundColor Cyan
    pip install uv
    Write-Host "✅ uv установлен!" -ForegroundColor Green
}
# Проверяем существование .venv
if (-not (Test-Path ".venv")) {
    Write-Host "🚀 Создаю виртуальное окружение..." -ForegroundColor Cyan
    uv venv
    Write-Host "✨ Виртуальное окружение создано!" -ForegroundColor Green

    # Активируем виртуальное окружение
    Write-Host "🔌 Активирую виртуальное окружение..." -ForegroundColor Cyan
    .\.venv\Scripts\Activate.ps1
    Write-Host "✅ Виртуальное окружение активировано!" -ForegroundColor Green

    # Устанавливаем зависимости только при первом создании venv
    Write-Host "📦 Устанавливаю зависимости..." -ForegroundColor Cyan
    uv pip install -e ".[dev]"
    Write-Host "🎉 Установка завершена успешно!" -ForegroundColor Green
}
else {
    # Только активируем существующее окружение
    Write-Host "🔌 Активирую виртуальное окружение..." -ForegroundColor Cyan
    .\.venv\Scripts\Activate.ps1
    Write-Host "✅ Виртуальное окружение активировано!" -ForegroundColor Green
}