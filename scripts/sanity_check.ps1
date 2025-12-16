# AN1 API Sanity Check Script
# Verifies API endpoint is accessible and accepts infer_z requests

Write-Host "AN1 API Sanity Check" -ForegroundColor Cyan
Write-Host "====================" -ForegroundColor Cyan
Write-Host ""

# Check required environment variables
if (-not $env:AN1_API_URL) {
    Write-Host "ERROR: AN1_API_URL environment variable is not set" -ForegroundColor Red
    Write-Host "Set it with: `$env:AN1_API_URL='https://your-domain.com/api/an1-turbo'" -ForegroundColor Yellow
    exit 1
}

if (-not $env:AN1_API_KEY) {
    Write-Host "ERROR: AN1_API_KEY environment variable is not set" -ForegroundColor Red
    Write-Host "Set it with: `$env:AN1_API_KEY='your-api-key'" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ AN1_API_URL: $env:AN1_API_URL" -ForegroundColor Green
Write-Host "✓ AN1_API_KEY: [REDACTED]" -ForegroundColor Green
Write-Host ""

# Create request payload with 256 zeros
Write-Host "Generating request payload (256-float z vector)..." -ForegroundColor Yellow
$z = @(0.0) * 256
$payload = @{
    mode = "infer_z"
    z = $z
} | ConvertTo-Json -Compress

# Write to temporary file
$requestFile = "request_sanity.json"
$payload | Out-File -Encoding utf8 -FilePath $requestFile
Write-Host "✓ Request payload written to $requestFile" -ForegroundColor Green
Write-Host ""

# Send request
Write-Host "Sending request to API..." -ForegroundColor Yellow
try {
    $response = curl.exe -i -sS -L -X POST "$env:AN1_API_URL" `
        -H "Content-Type: application/json" `
        -H "Authorization: Bearer $env:AN1_API_KEY" `
        --data-binary "@$requestFile"
    
    Write-Host ""
    Write-Host "Response:" -ForegroundColor Cyan
    Write-Host $response
    
    # Extract HTTP status code
    if ($response -match 'HTTP/\d\.\d\s+(\d+)') {
        $statusCode = $matches[1]
        Write-Host ""
        if ($statusCode -eq "200") {
            Write-Host "✓ Sanity check PASSED (HTTP $statusCode)" -ForegroundColor Green
            Write-Host ""
            Write-Host "API is accessible and accepts infer_z requests." -ForegroundColor Green
        } else {
            Write-Host "⚠ Sanity check returned HTTP $statusCode" -ForegroundColor Yellow
            Write-Host "Check the response body above for error details." -ForegroundColor Yellow
        }
    }
    
} catch {
    Write-Host ""
    Write-Host "ERROR: Failed to send request" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
} finally {
    # Clean up temporary file
    if (Test-Path $requestFile) {
        Remove-Item $requestFile -ErrorAction SilentlyContinue
    }
}

Write-Host ""

