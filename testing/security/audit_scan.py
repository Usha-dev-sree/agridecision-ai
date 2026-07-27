import yaml, glob, os, re, json

findings = []

def add(severity, category, loc, issue, recommendation):
    findings.append({'severity': severity, 'category': category, 'location': loc, 'issue': issue, 'recommendation': recommendation})

dc = open('docker-compose.yml').read()

# 1. Hardcoded secrets in docker-compose.yml
for secret in ['SecretPassword123', 'SecretRedis123']:
    if secret in dc:
        add('CRITICAL', 'SECRETS', 'docker-compose.yml', f'Hardcoded secret: "{secret}"', 'Use Docker secrets or Vault injection at runtime')

# 2. Vault in dev mode
if 'VAULT_DEV_ROOT_TOKEN_ID' in dc:
    add('CRITICAL', 'VAULT', 'docker-compose.yml', 'Vault running in dev mode with root token exposed', 'Use server mode with AppRole/Kubernetes auth; never expose root token')

if 'tls_disable' in dc:
    add('HIGH', 'VAULT', 'docker-compose.yml', 'Vault TLS disabled (tls_disable: 1)', 'Enable TLS with cert/key files in production Vault config')

# 3. Kong CORS wildcard
kong = open('devops/kong/kong.yml').read()
if '"*"' in kong or "'*'" in kong:
    add('HIGH', 'CORS', 'devops/kong/kong.yml', 'CORS origins set to wildcard (*)', 'Restrict to known frontend domains only')

if 'policy: local' in kong:
    add('MEDIUM', 'RATE_LIMITING', 'devops/kong/kong.yml', 'Rate limiting policy is "local" — not cluster-aware', 'Change to policy: redis for distributed rate limiting')

if 'jwt' not in kong.lower():
    add('HIGH', 'JWT', 'devops/kong/kong.yml', 'No JWT validation plugin on Kong gateway', 'Add Kong jwt plugin to validate tokens at gateway layer')

# 4. Kong admin API exposed
if '8001:8001' in dc:
    add('HIGH', 'EXPOSURE', 'docker-compose.yml', 'Kong admin API port 8001 exposed on host', 'Remove host port mapping; admin API must be internal-only')

# 5. FastAPI CORS wildcard
for svc_main in glob.glob('backend/services/*/src/main.py'):
    content = open(svc_main).read()
    if 'allow_origins=["*"]' in content:
        add('HIGH', 'CORS', svc_main, 'FastAPI CORS allows all origins (*)', 'Read ALLOWED_ORIGINS from environment; restrict to frontend domains')

# 6. JWT algorithm HS256
for conf in glob.glob('backend/services/*/src/config.py'):
    c = open(conf).read()
    if 'HS256' in c:
        add('MEDIUM', 'JWT', conf, 'JWT algorithm HS256 (symmetric)', 'Prefer RS256 asymmetric signing for multi-service validation without sharing secret')

# 7. Missing iss/aud in JWT
sec = open('backend/common/security.py').read()
if '"iss"' not in sec and "'iss'" not in sec:
    add('MEDIUM', 'JWT', 'backend/common/security.py', 'JWT tokens missing iss and aud claims', 'Add iss=agridecision.ai and aud claims; validate them on decode()')

# 8. OTP stored plaintext in Redis
repo = open('backend/services/user_service/src/repositories/session_repository.py').read()
if 'setex(key, ttl_seconds, otp)' in repo:
    add('MEDIUM', 'SECRETS', 'backend/services/user_service/src/repositories/session_repository.py',
        'OTP stored as plaintext in Redis', 'Store HMAC-SHA256 hash of OTP; compare hash on verify')

# 9. Missing blacklist check in get_current_user
deps = open('backend/common/dependencies.py').read()
if 'is_token_blacklisted' not in deps:
    add('HIGH', 'JWT', 'backend/common/dependencies.py',
        'get_current_user() does not check JWT token blacklist', 'Check token blacklist on every authenticated request')

# 10. datetime.utcnow() naive datetime
auth_svc = open('backend/services/user_service/src/services/auth_service.py').read()
if 'datetime.utcnow()' in auth_svc:
    add('LOW', 'SECURITY_HYGIENE', 'backend/services/user_service/src/services/auth_service.py',
        'datetime.utcnow() produces timezone-naive datetime', 'Use datetime.now(timezone.utc)')

# 11. GHA missing permissions block
gha = open('.github/workflows/ci-backend.yml').read()
if 'permissions:' not in gha:
    add('HIGH', 'GITHUB_ACTIONS', '.github/workflows/ci-backend.yml',
        'No permissions block — workflow has default broad repo write access', 'Add permissions: read-all at workflow level')

# 12. GHA mutable action tags
if 'codecov/codecov-action@v4' in gha:
    add('MEDIUM', 'GITHUB_ACTIONS', '.github/workflows/ci-backend.yml',
        'Third-party action pinned to mutable tag, not commit SHA', 'Pin all third-party actions to full commit SHA')

# 13. safety check deprecated
if 'safety check' in gha:
    add('LOW', 'GITHUB_ACTIONS', '.github/workflows/ci-backend.yml',
        '"safety check" uses deprecated API', 'Use "safety scan" or pip-audit')

# 14. Kafka PLAINTEXT
if 'PLAINTEXT:PLAINTEXT' in dc:
    add('HIGH', 'KAFKA', 'docker-compose.yml',
        'Kafka listener uses PLAINTEXT (no TLS, no auth)', 'Use SASL_SSL with certificates and SCRAM-SHA-512 in production')

# 15. Prometheus exposed
if '9090:9090' in dc:
    add('MEDIUM', 'EXPOSURE', 'docker-compose.yml',
        'Prometheus port 9090 exposed on host with no authentication', 'Remove host port; use ingress with OAuth2 proxy')

# 16. Grafana default password
if 'GF_SECURITY_ADMIN_PASSWORD=admin' in dc:
    add('CRITICAL', 'SECRETS', 'docker-compose.yml',
        'Grafana admin password is "admin" (default)', 'Inject strong password from Vault; enable auth proxy or OAuth2')

# 17. Redis no TLS in env example
env = open('.env.example').read()
if 'REDIS_URL=redis://' in env and 'rediss://' not in env:
    add('MEDIUM', 'REDIS', '.env.example',
        'Redis URL uses non-TLS redis:// scheme in example config', 'Use rediss:// (TLS) for Redis connections in production')

# 18. Elasticsearch plaintext in env example
if 'ELASTICSEARCH_URL=http://' in env:
    add('MEDIUM', 'EXPOSURE', '.env.example',
        'Elasticsearch URL uses HTTP (not HTTPS)', 'Use https:// for Elasticsearch in all non-local environments')

# 19. Missing security headers middleware
for svc_main in glob.glob('backend/services/*/src/main.py'):
    content = open(svc_main).read()
    if 'X-Content-Type-Options' not in content and 'SecurityHeadersMiddleware' not in content:
        add('MEDIUM', 'XSS', svc_main,
            'No security headers middleware (X-Content-Type-Options, X-Frame-Options, CSP missing)',
            'Add SecurityHeadersMiddleware to inject security headers on all responses')

# 20. Missing request size limit
for svc_main in glob.glob('backend/services/*/src/main.py'):
    content = open(svc_main).read()
    if 'max_request_size' not in content and 'RequestSizeLimitMiddleware' not in content:
        add('LOW', 'SSRF', svc_main,
            'No request body size limit configured', 'Add RequestSizeLimitMiddleware or set max_request_size to prevent DoS via large payloads')

print(json.dumps(findings, indent=2))
print()
print(f'Total findings: {len(findings)}')
severities = {}
for f in findings:
    severities[f['severity']] = severities.get(f['severity'], 0) + 1
for s in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
    print(f'  {s}: {severities.get(s, 0)}')
