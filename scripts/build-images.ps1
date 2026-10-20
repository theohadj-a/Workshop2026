param (
    [string]$Tag = "latest",
    [string]$Service = "all",
    [string]$Platform = "linux/amd64",
    [switch]$NoCache = $false
)

$ErrorActionPreference = "Stop"

function Log-Info { param([string]$msg) Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Log-Success { param([string]$msg) Write-Host "[SUCCESS] $msg" -ForegroundColor Green }
function Log-Warn { param([string]$msg) Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Log-Error { param([string]$msg) Write-Host "[ERROR] $msg" -ForegroundColor Red }

Clear-Host
Write-Host "==========================================================" -ForegroundColor Magenta
Write-Host "  PROJECT RESILIENCE-ALPHA - DOCKER IMAGE BUILDER         " -ForegroundColor Magenta
Write-Host "  Equipe : Theo, Mael, Flora, Fely, Aymeric               " -ForegroundColor Magenta
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
        Log-Error "Service inconnu : $Service. Options valides: all, payment-api, remediation-engine, dashboard-ui, aiops-detector."
        exit 1
    }
}

$BuildResults = @()
$TotalStopwatch = [System.Diagnostics.Stopwatch]::StartNew()

foreach ($s in $ServicesToBuild) {
    $ImageFull = "$($s.ImageName):$Tag"
    Write-Host ""
    Write-Host "----------------------------------------------------------" -ForegroundColor DarkGray
    Log-Info "Demarrage du build : $ImageFull (Dossier : $($s.Context), Plateforme : $Platform)"
    
    $BuildArgs = @("buildx", "build", "--platform", $Platform, "-t", $ImageFull, "--load", $s.Context)
    if ($NoCache) {
        $BuildArgs += "--no-cache"
        Log-Warn "Option --no-cache activee."
    }

    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $status = "OK"

    try {
        & docker $BuildArgs
        if ($LASTEXITCODE -ne 0) {
            throw "Erreur lors du build de l'image $($s.Name)"
        }
        $sw.Stop()
        $duration = [Math]::Round($sw.Elapsed.TotalSeconds, 1)
        Log-Success "Image $ImageFull construite avec succes en ${duration}s."
    } catch {
        $sw.Stop()
        $duration = [Math]::Round($sw.Elapsed.TotalSeconds, 1)
        $status = "FAILED"
        Log-Error "Echec du build pour $($s.Name)"
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
docker images --filter "reference=payment-api" --filter "reference=remediation-engine" --filter "reference=dashboard-ui" --filter "reference=aiops-detector"

Write-Host ""
Log-Success "Build termine ! Deploiement possible via Docker Compose ou Helm."
