<#
.SYNOPSIS
    Демонстрация этапа 3 проекта УВМ (вариант №2).
.DESCRIPTION
    Запускает примеры этапа и складывает результаты в output/.
#>

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = 'utf-8'
$Python = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    New-Item -ItemType Directory -Force -Path 'output' | Out-Null

    Write-Host '=== ТЕСТ: Этап 3 ==='
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

    Write-Host '--- 3. Копирование массива и JSON-дамп ---'
    & $Python src/assembler.py -i tests/copy_array.json `
        -o output/copy_array.bin
    & $Python src/interpreter.py -i output/copy_array.bin `
        -o output/copy_array.dump.json -r 0:19

    Write-Host ''
    Write-Host 'Готово: результаты в каталоге output.'
}
finally {
    Pop-Location
}
exit 0
