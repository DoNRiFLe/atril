# Instala el alineador de letras en un entorno virtual propio.
# Uso:  powershell -ExecutionPolicy Bypass -File tools\instalar-alineador.ps1
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$raiz = Split-Path -Parent $PSScriptRoot
$venv = Join-Path $raiz '.venv-alineador'

# --- no trabajar dentro de carpetas del sistema ---
if ($raiz -like "$env:WINDIR*" -or $raiz -like "$env:ProgramFiles*") {
    Write-Host ""
    Write-Host "Estas trabajando dentro de una carpeta del sistema:" -ForegroundColor Red
    Write-Host "  $raiz"
    Write-Host ""
    Write-Host "Windows te va a pedir permisos de administrador y algunas cosas van a fallar."
    Write-Host "Mové el proyecto a tu carpeta de usuario, por ejemplo:"
    Write-Host "  cd `$HOME" -ForegroundColor Cyan
    Write-Host "  git clone -b claude/amazing-thompson-mslhkg https://github.com/DoNRiFLe/preguntascumple" -ForegroundColor Cyan
    Write-Host "  cd preguntascumple" -ForegroundColor Cyan
    Write-Host ""
    $r = Read-Host "Seguir igual de todas formas? (s/N)"
    if ($r -ne 's' -and $r -ne 'S') { exit 1 }
}

# --- buscar un Python de verdad (el stub de la Microsoft Store no cuenta) ---
function Find-Python {
    $candidatos = @()
    foreach ($cmd in 'py', 'python', 'python3') {
        foreach ($c in (Get-Command $cmd -All -ErrorAction SilentlyContinue)) {
            if ($c.Source -and $c.Source -like '*WindowsApps*') { continue }  # stub de la Store
            if ($c.Source) { $candidatos += $c.Source } else { $candidatos += $c.Name }
        }
    }
    $candidatos += "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
    $candidatos += "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
    $candidatos += "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
    foreach ($exe in $candidatos) {
        try {
            $v = & $exe -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null
            if ($LASTEXITCODE -eq 0 -and $v -match '^3\.(\d+)$') {
                if ([int]$Matches[1] -ge 9) { return @{ Exe = $exe; Ver = $v } }
            }
        } catch {}
    }
    return $null
}

$python = Find-Python
if (-not $python) {
    Write-Host ""
    Write-Host "No encontre Python 3.9 o mas nuevo." -ForegroundColor Red
    Write-Host ""
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        $r = Read-Host "Lo instalo con winget ahora? (S/n)"
        if ($r -ne 'n' -and $r -ne 'N') {
            winget install --id Python.Python.3.12 -e --source winget `
                --accept-source-agreements --accept-package-agreements
            Write-Host ""
            Write-Host "Python instalado." -ForegroundColor Green
            Write-Host "CERRA esta ventana de PowerShell y abri una nueva" -ForegroundColor Yellow
            Write-Host "(el PATH no se actualiza en la sesion actual), y volve a correr:" -ForegroundColor Yellow
            Write-Host "  powershell -ExecutionPolicy Bypass -File tools\instalar-alineador.ps1" -ForegroundColor Cyan
            exit 0
        }
    }
    Write-Host "Instalalo a mano desde https://www.python.org/downloads/"
    Write-Host "y en el instalador MARCA la opcion 'Add python.exe to PATH'."
    exit 1
}

Write-Host "Python $($python.Ver) encontrado en $($python.Exe)" -ForegroundColor Green
Write-Host "Creando entorno en $venv ..." -ForegroundColor Cyan
& $python.Exe -m venv $venv

$vpy = Join-Path $venv 'Scripts\python.exe'
if (-not (Test-Path $vpy)) { $vpy = Join-Path $venv 'bin/python' }
if (-not (Test-Path $vpy)) {
    Write-Host "No se pudo crear el entorno virtual en $venv" -ForegroundColor Red
    Write-Host "Probá correr:  $($python.Exe) -m ensurepip --upgrade"
    exit 1
}

& $vpy -m pip install --upgrade pip --quiet
Write-Host "Instalando faster-whisper (baja unos 200 MB, aguanta)..." -ForegroundColor Cyan
& $vpy -m pip install -r (Join-Path $PSScriptRoot 'requirements.txt')
if ($LASTEXITCODE -ne 0) { Write-Host "Fallo la instalacion de dependencias." -ForegroundColor Red; exit 1 }

& $vpy -c "import faster_whisper; print('faster-whisper', faster_whisper.__version__, 'OK')"

# --- demucs, opcional: aisla la voz para los temas con la banda fuerte ---
Write-Host ""
Write-Host "Demucs aisla la voz del resto de la banda antes de transcribir."
Write-Host "Sirve para los temas donde Whisper no entiende nada."
Write-Host "Se trae PyTorch: unos 2,5 GB de descarga." -ForegroundColor Yellow
$r = Read-Host "Instalarlo tambien? (s/N)"
if ($r -eq 's' -or $r -eq 'S') {
    & $vpy -m pip install demucs
    if ($LASTEXITCODE -eq 0) {
        & $vpy -c "import demucs; print('demucs', demucs.__version__, 'OK')"
    } else {
        Write-Host "Fallo la instalacion de demucs. Podes reintentar despues con:" -ForegroundColor Yellow
        Write-Host "  $vpy -m pip install demucs"
    }
}

Write-Host ""
Write-Host "Listo." -ForegroundColor Green
Write-Host "Para alinear un tema, arrastra el audio sobre tools\alinear.bat"
Write-Host "(tiene que haber un .txt con la letra y el mismo nombre al lado)."
Write-Host "Si la banda tapa la voz, usa tools\alinear-voz-aislada.bat en su lugar."
Write-Host "A mano:"
Write-Host "  $vpy tools\alinear.py tema.mp3 tema.txt -o tema.lrc -m small" -ForegroundColor Cyan
