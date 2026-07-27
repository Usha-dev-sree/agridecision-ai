# ============================================================
# AgriDecision AI — Smoke Test (PowerShell)
# Tests all infrastructure, backend services, and frontend
# ============================================================

param(
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"
$passed = 0
$failed = 0
$total = 0

function Test-Endpoint {
    param([string]$Name, [string]$Url, [int]$ExpectedStatus = 200, [string]$ExpectedBody = "")
    $script:total++
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        $statusOk = $response.StatusCode -eq $ExpectedStatus
        $bodyOk = if ($ExpectedBody) { $response.Content -like "*$ExpectedBody*" } else { $true }
        if ($statusOk -and $bodyOk) {
            Write-Host "  [PASS] $Name" -ForegroundColor Green
            $script:passed++
        } else {
            Write-Host "  [FAIL] $Name (Status: $($response.StatusCode), Expected: $ExpectedStatus)" -ForegroundColor Red
            $script:failed++
        }
    } catch {
        Write-Host "  [FAIL] $Name - $($_.Exception.Message)" -ForegroundColor Red
        $script:failed++
    }
}

function Test-Docker {
    param([string]$ContainerName, [string]$ExpectedStatus = "healthy")
    $script:total++
    try {
        $status = docker inspect --format "{{.State.Health.Status}}" $ContainerName 2>$null
        if (-not $status) {
            $running = docker inspect --format "{{.State.Status}}" $ContainerName 2>$null
            if ($running -eq "running") {
                Write-Host "  [PASS] $ContainerName (running, no healthcheck)" -ForegroundColor Green
                $script:passed++
                return
            }
        }
        if ($status -eq $ExpectedStatus) {
            Write-Host "  [PASS] $ContainerName ($status)" -ForegroundColor Green
            $script:passed++
        } else {
            Write-Host "  [FAIL] $ContainerName (Status: $status, Expected: $ExpectedStatus)" -ForegroundColor Red
            $script:failed++
        }
    } catch {
        Write-Host "  [FAIL] $ContainerName - $($_.Exception.Message)" -ForegroundColor Red
        $script:failed++
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AGRIDECISION AI - SMOKE TEST" -ForegroundColor Cyan
Write-Host "  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# ── 1. Docker Infrastructure ──
Write-Host "`n--- Docker Infrastructure ---" -ForegroundColor Yellow
Test-Docker "agri-postgres"
Test-Docker "agri-timescaledb"
Test-Docker "agri-redis"
Test-Docker "agri-zookeeper"
Test-Docker "agri-kafka"
Test-Docker "agri-kong"
Test-Docker "agri-prometheus"
Test-Docker "agri-grafana"
Test-Docker "agri-loki"
Test-Docker "agri-tempo"
Test-Docker "agri-vault"

# ── 2. Backend Microservices Health ──
Write-Host "`n--- Backend Services (Health Check) ---" -ForegroundColor Yellow
Test-Endpoint "User Service"         "http://localhost:8009/health" 200 "user-service"
Test-Endpoint "Farm Service"         "http://localhost:8001/health" 200 "farm-service"
Test-Endpoint "Advisory Service"     "http://localhost:8002/health" 200 "advisory-service"
Test-Endpoint "Weather Service"      "http://localhost:8003/health" 200 "weather-service"
Test-Endpoint "Market Service"       "http://localhost:8004/health" 200 "market-service"
Test-Endpoint "Analytics Service"    "http://localhost:8005/health" 200 "analytics-service"
Test-Endpoint "Financial Service"    "http://localhost:8006/health" 200 "financial-service"
Test-Endpoint "Notification Service" "http://localhost:8007/health" 200 "notification-service"
Test-Endpoint "Enterprise Service"   "http://localhost:8008/health" 200 "enterprise-service"

# ── 3. API Docs (Swagger) ──
Write-Host "`n--- API Documentation (OpenAPI) ---" -ForegroundColor Yellow
Test-Endpoint "User API Docs"         "http://localhost:8009/v1/openapi.json" 200 "openapi"
Test-Endpoint "Farm API Docs"         "http://localhost:8001/v1/openapi.json" 200 "openapi"
Test-Endpoint "Advisory API Docs"     "http://localhost:8002/v1/openapi.json" 200 "openapi"
Test-Endpoint "Weather API Docs"      "http://localhost:8003/v1/openapi.json" 200 "openapi"
Test-Endpoint "Market API Docs"       "http://localhost:8004/v1/openapi.json" 200 "openapi"

# ── 4. Frontend ──
Write-Host "`n--- Frontend ---" -ForegroundColor Yellow
Test-Endpoint "Agronomist Portal" "http://localhost:5173" 200

# ── 5. Monitoring ──
Write-Host "`n--- Monitoring Stack ---" -ForegroundColor Yellow
Test-Endpoint "Prometheus"  "http://localhost:9090/-/ready" 200
Test-Endpoint "Grafana"     "http://localhost:3005/api/health" 200

# ── 6. Database Connectivity ──
Write-Host "`n--- Database Validation ---" -ForegroundColor Yellow
$script:total++
try {
    $result = "SELECT count(*) FROM reference.crop_variety;" | docker exec -i agri-postgres psql -U postgres -d agridecision_user -t 2>$null
    $rawStr = ($result | Out-String).Trim()
    if ($rawStr -match "(\d+)") {
        $count = [int]$Matches[1]
        if ($count -ge 20) {
            Write-Host "  [PASS] PostgreSQL seed data verified ($count crop varieties)" -ForegroundColor Green
            $script:passed++
        } else {
            Write-Host "  [FAIL] PostgreSQL seed data incomplete ($count crop varieties)" -ForegroundColor Red
            $script:failed++
        }
    } else {
        Write-Host "  [FAIL] Could not parse crop variety count: $rawStr" -ForegroundColor Red
        $script:failed++
    }
} catch {
    Write-Host "  [FAIL] PostgreSQL connectivity - $($_.Exception.Message)" -ForegroundColor Red
    $script:failed++
}

$script:total++
try {
    $result = "SELECT count(*) FROM iam.""user"";" | docker exec -i agri-postgres psql -U postgres -d agridecision_user -t 2>$null
    $rawStr = ($result | Out-String).Trim()
    if ($rawStr -match "(\d+)") {
        $count = [int]$Matches[1]
        if ($count -ge 3) {
            Write-Host "  [PASS] User data verified ($count users)" -ForegroundColor Green
            $script:passed++
        } else {
            Write-Host "  [FAIL] User data incomplete ($count users)" -ForegroundColor Red
            $script:failed++
        }
    } else {
        Write-Host "  [FAIL] Could not parse user count: $rawStr" -ForegroundColor Red
        $script:failed++
    }
} catch {
    Write-Host "  [FAIL] User data check - $($_.Exception.Message)" -ForegroundColor Red
    $script:failed++
}

$script:total++
try {
    $redisOk = docker exec agri-redis redis-cli -a SecretRedis123 ping 2>$null
    if ($redisOk -match "PONG") {
        Write-Host "  [PASS] Redis connectivity (PONG)" -ForegroundColor Green
        $script:passed++
    } else {
        Write-Host "  [FAIL] Redis not responding" -ForegroundColor Red
        $script:failed++
    }
} catch {
    Write-Host "  [FAIL] Redis - $($_.Exception.Message)" -ForegroundColor Red
    $script:failed++
}

# ── Summary ──
Write-Host "`n============================================" -ForegroundColor Cyan
$color = if ($failed -eq 0) { "Green" } else { "Red" }
Write-Host "  RESULTS: $passed/$total passed, $failed failed" -ForegroundColor $color
if ($failed -eq 0) {
    Write-Host "  STATUS: ALL TESTS PASSED" -ForegroundColor Green
} else {
    Write-Host "  STATUS: SOME TESTS FAILED" -ForegroundColor Red
}
Write-Host "============================================`n" -ForegroundColor Cyan

exit $failed
