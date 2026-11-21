<#
.SYNOPSIS
    Демонстрация этапа 5 проекта УВМ (вариант №2).
.DESCRIPTION
    Запускает примеры этапа и складывает результаты в output/.
#>

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = 'utf-8'
$Python = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    New-Item -ItemType Directory -Force -Path 'output' | Out-Null

    Write-Host '=== ТЕСТ: Этап 5 ==='
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

    Write-Host '--- 4. Унарная операция bitreverse() ---'
    & $Python src/assembler.py -i tests/test_bitreverse.json `
        -o output/test_bitreverse.bin
    & $Python src/interpreter.py `
        -i output/test_bitreverse.bin `
        -o output/test_bitreverse.dump.json -r 200:205
    & $Python src/interpreter.py `
        -i output/test_bitreverse.bin `
        -o output/test_bitreverse.source.json -r 110:115

    Write-Host '--- 5. Тестовая задача: три примера ---'
    foreach ($Case in 1, 2, 3) {
        $Program = "task_vector8_case$Case"
        Write-Host "-- $Program --"
        & $Python src/assembler.py -i "tests/$Program.json" `
            -o "output/$Program.bin"
        & $Python src/interpreter.py -i "output/$Program.bin" `
            -o "output/$Program.dump.json" -r 0:4095
    }
    Write-Host ''
    Write-Host '--- 6. Проверка инволютивности bitreverse ---'
    & $Python src/interpreter.py `
        -i output/task_vector8_case3.bin `
        -o output/task_vector8_case3.involution.json -r 400:400

    Write-Host ''
    Write-Host 'Готово: результаты в каталоге output.'
}
finally {
    Pop-Location
}
exit 0
