#!/usr/bin/env bash
set -e

echo "Initializing HashiCorp Vault Secrets Engine..."

export VAULT_ADDR="http://localhost:8200"
export VAULT_TOKEN="root-token"

# Enable Key-Value secret engine v2
vault secrets enable -path=secret kv-v2 || true

# Insert database secrets
vault kv put secret/data/postgres \
  username="postgres" \
  password="SecretPassword123" \
  host="postgres" \
  port="5432"

# Insert Redis secrets
vault kv put secret/data/redis \
  password="SecretRedis123" \
  host="redis" \
  port="6379"

# Insert JWT secret keys
vault kv put secret/data/jwt \
  secret_key="super-secret-jwt-key-change-in-prod" \
  algorithm="HS256"

echo "Vault secrets successfully populated!"
