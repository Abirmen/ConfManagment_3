<#
.SYNOPSIS
    Демонстрация этапа 2 проекта УВМ (вариант №2).
.DESCRIPTION
    Запускает примеры этапа и складывает результаты в output/.
#>

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = 'utf-8'
$Python = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    New-Item -ItemType Directory -Force -Path 'output' | Out-Null

    Write-Host '=== ТЕСТ: Этап 2 ==='
    Write-Host ''

    Write-Host '--- 1. Режим тестирования: байты команд ---'
    Write-Host 'Параметры: -i tests/spec_tests.json -o output/spec_tests.bin -t'
    Write-Host ''
    & $Python src/assembler.py -i tests/spec_tests.json `
        -o output/spec_tests.bin -t
    Write-Host ''
    Write-Host '--- 2. Обычный запуск без режима тестирования ---'
    & $Python src/assembler.py -i tests/spec_tests.json `
        -o output/spec_tests.bin

    Write-Host ''
    Write-Host '--- Ошибка: исходный файл не найден ---'
    & $Python src/assembler.py -i tests/missing.json `
        -o output/missing.ir.txt

    Write-Host ''
    Write-Host 'Готово: результаты в каталоге output.'
}
finally {
    Pop-Location
}
exit 0
