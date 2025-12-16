# AN1 API Sanity Check
# Validates API endpoint accessibility and infer_z request acceptance

if (-not $env:AN1_API_URL) {
    Write-Error "AN1_API_URL is not set"
    exit 1
}

if (-not $env:AN1_API_KEY) {
    Write-Error "AN1_API_KEY is not set"
    exit 1
}

# Build a deterministic 256-dim z vector (all zeros for simplicity)
$z = @(0..255 | ForEach-Object { 0.0 })

$body = @{
    mode = "infer_z"
    z    = $z
} | ConvertTo-Json -Compress

try {
    $response = Invoke-RestMethod `
        -Method Post `
        -Uri $env:AN1_API_URL `
        -Headers @{ Authorization = "Bearer $env:AN1_API_KEY" } `
        -ContentType "application/json" `
        -Body $body

    if ($response.ok -ne $true) {
        Write-Error "Sanity check failed: API returned ok=false"
        exit 1
    }

    Write-Host "Sanity check passed." -ForegroundColor Green
    Write-Host "Mode:" $response.mode
    Write-Host "Backend:" $response.backend
    Write-Host "Latency (ms):" $response.latency_ms
    exit 0
}
catch {
    Write-Error "Sanity check failed:"
    Write-Error $_
    exit 1
}
