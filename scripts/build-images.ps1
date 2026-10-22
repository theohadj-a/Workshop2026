param (
    [string]$Tag = "latest",
    [string]$Service = "all",
    [string]$Platform = "",
    [switch]$NoCache = $false,
    [switch]$NoKindLoad = $false,
    [string]$KindCluster = ""
)

$ErrorActionPreference = "Stop"

# Détection automatique de la plateforme linux selon l'environnement PowerShell
if ([string]::IsNullOrWhiteSpace($Platform)) {
    $arch = if ($env:PROCESSOR_ARCHITECTURE -match "ARM64") { "arm64" } else { "amd64" }
    $Platform = "linux/$arch"
}

# Détection automatique et sécurisée d'un cluster Kind actif
if (-not $NoKindLoad -and [string]::IsNullOrWhiteSpace($KindCluster)) {
    if (Get-Command kind -ErrorAction SilentlyContinue) {
        try {
            $rawClusters = cmd /c "kind get clusters 2>nul"
            if (-not [string]::IsNullOrWhiteSpace($rawClusters)) {
                $firstCluster = ($rawClusters -split "`r?`n")[0]
                if (-not [string]::IsNullOrWhiteSpace($firstCluster) -and $firstCluster -notmatch "No kind clusters") {
                    $KindCluster = $firstCluster.Trim()
                }
            }
        } catch {
            $KindCluster = $null
        }
    }
}

function Log-Info { param([string]$msg) Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Log-Success { param([string]$msg) Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function Log-Warn { param([string]$msg) Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Log-Error { param([string]$msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }

Clear-Host
Write-Host "==========================================================" -ForegroundColor Magenta
Write-Host "  PROJECT RESILIENCE-ALPHA - DOCKER IMAGE BUILDER         " -ForegroundColor Magenta
Write-Host "  Equipe : Theo, Mael, Flora, Fely, Aymeric               " -ForegroundColor Magenta
Write-Host "  Plateforme cible : $Platform | Tag : $Tag               " -ForegroundColor Magenta
if ($KindCluster) {
    Write-Host "  Cluster Kind cible : $KindCluster (auto-load actif)      " -ForegroundColor Magenta
}
Write-Host "==========================================================" -ForegroundColor Magenta
Write-Host ""

Log-Info "Verification de la disponibilite du moteur Docker..."
try {
    docker info 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker engine not reachable"
    }
    Log-Success "Moteur Docker actif et pret."
} catch {
    Log-Error "Docker Desktop n'est pas demarre ou inaccessible."
    Log-Warn "Veuillez lancer Docker Desktop depuis le menu Demarrer."
    exit 1
}

$RootDir = Split-Path -Parent $PSScriptRoot

$ServicesToBuild = @(
    @{
        Name = "payment-api"
        Context = "services/payment-api"
        ImageName = "payment-api"
    },
    @{
        Name = "remediation-engine"
        Context = "services/remediation-engine"
        ImageName = "remediation-engine"
    },
    @{
        Name = "auth-service"
        Context = "services/auth-service"
        ImageName = "auth-service"
    },
    @{
        Name = "dashboard-ui"
        Context = "services/dashboard-ui"
        ImageName = "dashboard-ui"
    },
    @{
        Name = "aiops-detector"
        Context = "ai-ops/detector"
        ImageName = "aiops-detector"
    }
)

if ($Service -ne "all") {
    $ServicesToBuild = $ServicesToBuild | Where-Object { $_.Name -eq $Service }
    if ($ServicesToBuild.Count -eq 0) {
        Log-Error "Service inconnu : $Service. Options valides: all, payment-api, remediation-engine, auth-service, dashboard-ui, aiops-detector."
        exit 1
    }
}

$BuildResults = @()
$TotalStopwatch = [System.Diagnostics.Stopwatch]::StartNew()

foreach ($s in $ServicesToBuild) {
    $ImageFull = "$($s.ImageName):$Tag"
    $TargetDir = Join-Path $RootDir $s.Context
    
    Write-Host ""
    Write-Host "----------------------------------------------------------" -ForegroundColor DarkGray
    Log-Info "Demarrage du build : $ImageFull dans $($s.Context) (Plateforme : $Platform)"

    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $status = "OK"

    Push-Location $TargetDir
    try {
        $BuildArgs = @("buildx", "build", "--platform", $Platform, "-t", $ImageFull)
        if ($NoCache) {
            $BuildArgs += "--no-cache"
            Log-Warn "Option --no-cache activee."
        }
        $BuildArgs += @("--load", ".")

        & docker $BuildArgs
        if ($LASTEXITCODE -ne 0) {
            throw "Erreur lors du build de l'image $($s.Name)"
        }
        $sw.Stop()
        $duration = [Math]::Round($sw.Elapsed.TotalSeconds, 1)
        Log-Success "Image $ImageFull construite avec succes en ${duration}s."

        # Injection automatique dans Kind pour accès immédiat par Helm
        if ($KindCluster) {
            Log-Info "Injection de $ImageFull dans le cluster Kind '$KindCluster'..."
            & kind load docker-image $ImageFull --name $KindCluster
            Log-Success "Image $ImageFull injectee dans Kind avec succes."
        }
    } catch {
        $sw.Stop()
        $duration = [Math]::Round($sw.Elapsed.TotalSeconds, 1)
        $status = "FAILED"
        Log-Error "Echec du build pour $($s.Name) : $_"
    } finally {
        Pop-Location
    }

    $BuildResults += [PSCustomObject]@{
        Service = $s.Name
        Image = $ImageFull
        DurationSec = $duration
        Status = $status
    }
}

$TotalStopwatch.Stop()
$TotalDuration = [Math]::Round($TotalStopwatch.Elapsed.TotalSeconds, 1)

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Magenta
Write-Host "                    RESUME DU BUILD                       " -ForegroundColor Magenta
Write-Host "==========================================================" -ForegroundColor Magenta
$BuildResults | Format-Table -AutoSize

Write-Host "Duree totale du build : ${TotalDuration}s" -ForegroundColor Cyan
Write-Host ""

Log-Info "Images Docker locales disponibles :"
docker images --filter "reference=payment-api" --filter "reference=remediation-engine" --filter "reference=auth-service" --filter "reference=dashboard-ui" --filter "reference=aiops-detector"

if ($KindCluster) {
    Write-Host ""
    Log-Success "Toutes les images sont injectees dans le cluster Kind '$KindCluster'."
    Log-Info "Helm peut desormais instancier les pods sans ImagePullBackOff (pullPolicy: IfNotPresent)."
}

Write-Host ""
Log-Success "Build termine ! Deploiement pret pour Helm."
