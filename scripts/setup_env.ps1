$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")
$VenvPath = Join-Path $RepoRoot ".venv"
$RequirementsPath = Join-Path $RepoRoot "requirements-dev.txt"

function Get-PythonVersion {
    param([string] $PythonCommand)

    $code = "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
    try {
        $version = Invoke-Python -PythonCommand $PythonCommand -Arguments @("-c", $code) 2>$null
        if ($LASTEXITCODE -eq 0 -and $version) {
            return [string] $version
        }
    }
    catch {
        return $null
    }

    return $null
}

function Test-CompatiblePython {
    param([string] $PythonCommand)

    $code = "import sys; raise SystemExit(0 if (sys.version_info >= (3, 12) and sys.version_info < (3, 13)) else 1)"
    try {
        Invoke-Python -PythonCommand $PythonCommand -Arguments @("-c", $code) 2>$null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

function Resolve-Python {
    if ($env:AGROIA_PYTHON) {
        if (Test-CompatiblePython $env:AGROIA_PYTHON) {
            return $env:AGROIA_PYTHON
        }

        $version = Get-PythonVersion $env:AGROIA_PYTHON
        throw "AGROIA_PYTHON points to '$($env:AGROIA_PYTHON)', but it is not Python >=3.12,<3.13. Detected: $version"
    }

    $candidates = @(
        "py -3.12",
        "python3.12",
        "python"
    )

    foreach ($candidate in $candidates) {
        if (Test-CompatiblePython $candidate) {
            return $candidate
        }
    }

    throw "Python >=3.12,<3.13 was not found. Install Python 3.12 or set AGROIA_PYTHON to the full python.exe path."
}

function Invoke-Python {
    param(
        [string] $PythonCommand,
        [string[]] $Arguments
    )

    $parts = $PythonCommand -split " "
    $exe = $parts[0]
    $prefixArgs = @()
    if ($parts.Count -gt 1) {
        $prefixArgs = $parts[1..($parts.Count - 1)]
    }

    & $exe @prefixArgs @Arguments
}

$Python = Resolve-Python
$PythonVersion = Get-PythonVersion $Python
Write-Host "Using Python $PythonVersion via '$Python'"

if (-not (Test-Path -LiteralPath $VenvPath)) {
    Write-Host "Creating virtual environment at $VenvPath"
    Invoke-Python -PythonCommand $Python -Arguments @("-m", "venv", $VenvPath)
}
else {
    Write-Host "Virtual environment already exists at $VenvPath"
}

$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
if (-not (Test-Path -LiteralPath $VenvPython)) {
    throw "Virtual environment Python was not found at $VenvPython"
}

Write-Host "Upgrading packaging tools"
& $VenvPython -m pip install --upgrade pip setuptools wheel

Write-Host "Installing development dependencies from $RequirementsPath"
& $VenvPython -m pip install -r $RequirementsPath

Write-Host ""
Write-Host "Environment ready."
Write-Host "Activate: .\.venv\Scripts\Activate.ps1"
Write-Host "Tests:    python -m pytest -q"
Write-Host "Lint:     python -m ruff check src tests"
