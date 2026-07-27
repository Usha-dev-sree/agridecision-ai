#!/usr/bin/env bash
# =============================================
# AgriDecision AI — Post-Deployment Smoke Tests
# =============================================
# Usage: bash scripts/ops/smoke_test.sh [DOMAIN]
# Default DOMAIN: https://api.agridecision.ai

set -euo pipefail

DOMAIN="${1:-https://api.agridecision.ai}"
PASS=0
FAIL=0
TIMEOUT=10

echo "========================================"
echo "AgriDecision AI — Post-Deployment Smoke Tests"
echo "Target: ${DOMAIN}"
echo "========================================"

# ── Helper Functions ──────────────────────────────────────────────────────────
check_endpoint() {
  local name="$1"
  local url="$2"
  local expected_status="$3"
  local method="${4:-GET}"

  actual_status=$(curl -s -o /dev/null -w "%{http_code}" \
    --max-time "${TIMEOUT}" \
    -X "${method}" \
    "${url}" 2>/dev/null || echo "000")

  if [ "${actual_status}" -eq "${expected_status}" ]; then
    echo "  ✅ PASS  [${name}] — HTTP ${actual_status}"
    PASS=$((PASS + 1))
  else
    echo "  ❌ FAIL  [${name}] — Expected ${expected_status}, Got ${actual_status}"
    FAIL=$((FAIL + 1))
  fi
}

# ── 1. API Gateway Health ─────────────────────────────────────────────────────
echo ""
echo "── Section 1: API Gateway & Core Routes ──"
check_endpoint "API Gateway Root" "${DOMAIN}/" 404
check_endpoint "Auth OTP CORS Preflight" "${DOMAIN}/v1/auth/request-otp" 405 OPTIONS

# ── 2. Service Readiness Probes ───────────────────────────────────────────────
echo ""
echo "── Section 2: Microservice Readiness Probes ──"
SERVICES=("auth" "plots" "advisory" "market" "weather" "notifications")
for service in "${SERVICES[@]}"; do
  check_endpoint "${service}-service readiness" "${DOMAIN}/v1/${service}/healthz/readiness" 200
done

# ── 3. Authenticated Advisory Route ──────────────────────────────────────────
echo ""
echo "── Section 3: Protected Route Authentication Enforcement ──"
check_endpoint "Advisory without JWT" "${DOMAIN}/v1/advisory/crop-recommendations" 401
check_endpoint "Market prices (public)" "${DOMAIN}/v1/market/prices?state_code=IN-MH" 200

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "========================================"
echo "Smoke Test Results:"
echo "  PASSED: ${PASS}"
echo "  FAILED: ${FAIL}"
echo "========================================"

if [ "${FAIL}" -gt 0 ]; then
  echo "CRITICAL: ${FAIL} smoke tests failed. Deployment may need rollback."
  exit 1
fi

echo "All smoke tests passed. Deployment verified."
exit 0
