# AgriDecision AI — Security & Governance Compliance Report

## Security Audit Results
- **Authentication**: JWT token verification signed with RS256 algorithm.
- **Authorization**: RBAC policies verified across Farmer, Agronomist, Enterprise, and Admin roles.
- **CORS & Headers**: Strict CORS origin limits, HSTS, CSP, and X-Content-Type-Options headers active.
- **Rate Limiting**: Kong API Gateway enforces 100 requests/minute per client IP.
- **Vault Secrets**: API keys, database credentials, and RSA private keys isolated in HashiCorp Vault.
- **Data Protection**: AES-256 encryption at rest for PII and TLS 1.3 in transit.
