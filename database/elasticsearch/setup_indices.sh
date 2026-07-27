#!/usr/bin/env bash
# ============================================================
# AgriDecision AI — Elasticsearch Index Setup Script
# ============================================================
# Usage: bash database/elasticsearch/setup_indices.sh [ES_HOST]
# Default ES_HOST: http://localhost:9200
# ============================================================

set -euo pipefail

ES_HOST="${1:-http://localhost:9200}"
MAPPINGS_FILE="$(dirname "$0")/004_elasticsearch_mappings.json"
PASS=0
FAIL=0

echo "=========================================="
echo "AgriDecision AI — Elasticsearch Index Setup"
echo "Host: ${ES_HOST}"
echo "=========================================="

# ── Helper: Create or Update Index ────────────────────────────────────────────
create_index() {
  local index_name="$1"
  local settings_body="$2"

  echo ""
  echo "── Creating index: ${index_name} ──"

  # Delete existing index if it exists (dev only — gate this in production)
  if curl -s -o /dev/null -w "%{http_code}" "${ES_HOST}/${index_name}" | grep -q "200"; then
    echo "  [INFO] Index ${index_name} already exists. Skipping (use --force to recreate)."
    PASS=$((PASS + 1))
    return
  fi

  http_status=$(curl -s -o /tmp/es_response.json -w "%{http_code}" \
    -X PUT "${ES_HOST}/${index_name}" \
    -H "Content-Type: application/json" \
    -d "${settings_body}")

  if [ "${http_status}" -eq 200 ] || [ "${http_status}" -eq 201 ]; then
    echo "  ✅ Created: ${index_name} (HTTP ${http_status})"
    PASS=$((PASS + 1))
  else
    echo "  ❌ FAILED: ${index_name} (HTTP ${http_status})"
    cat /tmp/es_response.json
    FAIL=$((FAIL + 1))
  fi
}

# ── 1. Market Directory Index ──────────────────────────────────────────────────
create_index "agridecision_market_directory" '{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "analysis": {
      "analyzer": {
        "mandi_name_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "asciifolding", "edge_ngram_filter"]
        },
        "autocomplete_search_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "asciifolding"]
        }
      },
      "filter": {
        "edge_ngram_filter": {
          "type": "edge_ngram",
          "min_gram": 2,
          "max_gram": 15
        }
      }
    }
  },
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "mandi_code":     {"type": "keyword"},
      "mandi_name":     {"type": "text", "analyzer": "mandi_name_analyzer", "search_analyzer": "autocomplete_search_analyzer", "fields": {"keyword": {"type": "keyword"}}},
      "state_code":     {"type": "keyword"},
      "state_name":     {"type": "keyword"},
      "district_name":  {"type": "keyword"},
      "market_type":    {"type": "keyword"},
      "primary_crops":  {"type": "keyword"},
      "operating_days": {"type": "keyword"},
      "is_active":      {"type": "boolean"},
      "location":       {"type": "geo_point"},
      "latest_prices":  {"type": "nested", "properties": {"crop_code": {"type": "keyword"}, "crop_name": {"type": "text"}, "modal_price_inr": {"type": "float"}, "price_date": {"type": "date", "format": "yyyy-MM-dd"}}},
      "contact_phone":  {"type": "keyword", "index": false},
      "updated_at":     {"type": "date"}
    }
  }
}'

# ── 2. Advisory Knowledge Base Index ──────────────────────────────────────────
create_index "agridecision_advisory_knowledge_base" '{
  "settings": {
    "number_of_shards": 2,
    "number_of_replicas": 1
  },
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "article_id":   {"type": "keyword"},
      "title":        {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
      "content":      {"type": "text"},
      "summary":      {"type": "text"},
      "category":     {"type": "keyword"},
      "tags":         {"type": "keyword"},
      "language":     {"type": "keyword"},
      "crop_codes":   {"type": "keyword"},
      "pest_codes":   {"type": "keyword"},
      "state_codes":  {"type": "keyword"},
      "season_types": {"type": "keyword"},
      "source":       {"type": "keyword"},
      "author":       {"type": "keyword"},
      "published_at": {"type": "date"},
      "updated_at":   {"type": "date"},
      "view_count":   {"type": "integer"},
      "is_published": {"type": "boolean"}
    }
  }
}'

# ── 3. Crop Catalogue Index ────────────────────────────────────────────────────
create_index "agridecision_crop_catalogue" '{
  "settings": {
    "number_of_shards": 2,
    "number_of_replicas": 1
  },
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "crop_code":             {"type": "keyword"},
      "variety_code":          {"type": "keyword"},
      "common_name":           {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
      "scientific_name":       {"type": "text"},
      "local_names":           {"type": "object", "properties": {"en": {"type": "text"}, "hi": {"type": "text"}, "mr": {"type": "text"}, "te": {"type": "text"}, "ta": {"type": "text"}, "kn": {"type": "text"}}},
      "season":                {"type": "keyword"},
      "duration_days_min":     {"type": "integer"},
      "duration_days_max":     {"type": "integer"},
      "water_requirement_mm":  {"type": "float"},
      "suitable_aez_codes":    {"type": "keyword"},
      "suitable_soil_types":   {"type": "keyword"},
      "ph_min":                {"type": "float"},
      "ph_max":                {"type": "float"},
      "government_notified":   {"type": "boolean"},
      "msp_inr_per_quintal":   {"type": "float"},
      "updated_at":            {"type": "date"}
    }
  }
}'

# ── 4. Pest & Disease Catalogue Index ─────────────────────────────────────────
create_index "agridecision_pest_disease_catalogue" '{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1
  },
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "pest_code":           {"type": "keyword"},
      "common_name":         {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
      "scientific_name":     {"type": "text"},
      "local_names":         {"type": "object", "properties": {"en": {"type": "text"}, "hi": {"type": "text"}, "mr": {"type": "text"}}},
      "category":            {"type": "keyword"},
      "affected_crops":      {"type": "keyword"},
      "symptoms":            {"type": "text"},
      "management_organic":  {"type": "text"},
      "image_class_label":   {"type": "keyword"},
      "management_chemical": {"type": "nested", "properties": {"active_ingredient": {"type": "keyword"}, "dose": {"type": "text"}, "waiting_period_days": {"type": "integer"}}}
    }
  }
}'

# ── Index Aliases ──────────────────────────────────────────────────────────────
echo ""
echo "── Setting up read aliases ──"
curl -s -X POST "${ES_HOST}/_aliases" -H "Content-Type: application/json" -d '{
  "actions": [
    {"add": {"index": "agridecision_market_directory",       "alias": "market_directory"}},
    {"add": {"index": "agridecision_advisory_knowledge_base","alias": "advisory_kb"}},
    {"add": {"index": "agridecision_crop_catalogue",         "alias": "crop_catalogue"}},
    {"add": {"index": "agridecision_pest_disease_catalogue", "alias": "pest_catalogue"}}
  ]
}' | python3 -m json.tool

# ── Summary ────────────────────────────────────────────────────────────────────
echo ""
echo "=========================================="
echo "Elasticsearch Setup Results:"
echo "  PASSED: ${PASS}"
echo "  FAILED: ${FAIL}"
echo "=========================================="

[ "${FAIL}" -gt 0 ] && exit 1
echo "All Elasticsearch indices created and aliases configured."
exit 0
