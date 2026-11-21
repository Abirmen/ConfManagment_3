<#
.SYNOPSIS
    Запуск ассемблера, интерпретатора и тестов УВМ (вариант №2).
.DESCRIPTION
    Команды:
      assemble  <программа.json> <программа.bin>  [-Test]
      interpret <программа.bin> <дамп.json>  [-Range START:END]
      test
      demo
.EXAMPLE
    .\run.ps1 assemble tests\spec_tests.json output\spec_tests.bin -Test
.EXAMPLE
    .\run.ps1 demo
#>

param(
    [Parameter(Position = 0)]
    [ValidateSet('assemble', 'interpret', 'test', 'demo')]
    [string]$Command = 'demo',
    [Parameter(Position = 1)]
    [string]$Source,
    [Parameter(Position = 2)]
    [string]$Target,
    [string]$Range = '0:31',
    [switch]$Test
)

$previousConsole = [Console]::OutputEncoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$previousEncoding = $env:PYTHONIOENCODING
$env:PYTHONIOENCODING = 'utf-8'
$python = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

function Invoke-Python([string[]]$StepArgs) {
    & $script:python @StepArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Команда завершилась с кодом $LASTEXITCODE"
        exit $LASTEXITCODE
    }
}

function Invoke-Assemble {
    if (-not $Source -or -not $Target) {
        Write-Host 'Укажите входной и выходной файлы.'
        exit 2
    }
    $StepArgs = @('src/assembler.py', '-i', $Source, '-o', $Target)
    if ($Test) {
        $StepArgs += '-t'
    }
    Invoke-Python $StepArgs
}

function Invoke-Interpret {
    if (-not $Source -or -not $Target) {
        Write-Host 'Укажите входной и выходной файлы.'
        exit 2
    }
    Invoke-Python @('src/interpreter.py', '-i', $Source,
        '-o', $Target, '-r', $Range)
}

function Invoke-Tests {
    Invoke-Python @('-m', 'unittest', 'discover', '-s', 'tests', '-v')
}

function Invoke-Demo {
    New-Item -ItemType Directory -Force -Path 'output' | Out-Null
    Write-Host '== Тест спецификации (Этап 2) =='
    Invoke-Python @('src/assembler.py', '-i', 'tests/spec_tests.json',
        '-o', 'output/spec_tests.bin', '-t')
    Write-Host ''
    Write-Host '== Копирование массива (Этап 3) =='
    Invoke-Python @('src/assembler.py', '-i', 'tests/copy_array.json',
        '-o', 'output/copy_array.bin')
    Invoke-Python @('src/interpreter.py', '-i', 'output/copy_array.bin',
        '-o', 'output/copy_array.dump.json', '-r', '0:19')
}

Push-Location (Split-Path -Parent $PSScriptRoot)
try {
    switch ($Command) {
        'assemble' { Invoke-Assemble }
        'interpret' { Invoke-Interpret }
        'test' { Invoke-Tests }
        'demo' { Invoke-Demo }
    }
}
finally {
    Pop-Location
    $env:PYTHONIOENCODING = $previousEncoding
    [Console]::OutputEncoding = $previousConsole
}
