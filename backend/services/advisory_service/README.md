# Advisory Service

The Advisory Service is the intelligence core of AgriDecision AI, providing:
- **AI Crop Recommendations** – Rule-based + Triton ML inference pipeline
- **Irrigation Scheduling** – FAO-56 Penman-Monteith ETo calculation using live weather data
- **Plant Disease Diagnosis** – Vision model inference via Triton, async polling architecture

## Technology Stack
- FastAPI + asyncpg + SQLAlchemy 2.x
- Open-Meteo (weather forecasting, free tier)
- Triton Inference Server (gRPC for ML models)
- Kafka (async diagnosis jobs + analytics)
- Redis (recommendation caching)

## Key Algorithms
- **Penman-Monteith ETo** (FAO-56): `src/engines/irrigation_engine.py`
- **Crop Suitability Rules**: `src/engines/recommendation_engine.py`

## Environment Variables
See `src/config.py` for all required environment variables.
